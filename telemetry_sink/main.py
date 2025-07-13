import asyncio
import logging
import uvicorn


from telemetry_sink.app_builder.config import load_config
from telemetry_sink.app_builder.factory import (
    create_telemetry_service,
    create_log_writer,
    create_flush_timer,
    create_api_app,
    create_crypto_service,
)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


async def main():
    """
    The main asynchronous entry point for the Telemetry Sink.

    This function initializes all services, runs them concurrently, and handles
    the graceful shutdown sequence.
    """
    log.info("--- Telemetry Sink Starting Up ---")

    # 1. Load Configuration
    config = load_config()

    # 2. Build Services using Factories
    # This process wires up all the application's components.
    try:
        telemetry_service = create_telemetry_service(config)
        crypto_service = create_crypto_service(config)
        log_writer = create_log_writer(config, telemetry_service.buffer_manager, crypto_service)
        flush_timer = create_flush_timer(config, telemetry_service.buffer_manager)

        # Inject the core service into the API adapter to create the FastAPI app
        server_protocol = config.get("telemetry_sink_server", "protocol", fallback="http")
        server_port = config.get("telemetry_sink_server", "port")
        server_host = config.get("telemetry_sink_server", "bind_address")
        server = create_api_app(
            telemetry_service=telemetry_service,
            host=server_host,
            port=int(server_port),
            server_protocol=server_protocol,
        )
    except (ValueError, KeyError) as e:
        log.critical(f"FATAL: Failed to initialize services due to invalid config value. Error: {e}")
        return

    # 3. Run Services Concurrently and Handle Shutdown
    try:
        log.info("Starting all concurrent services...")
        # asyncio.gather runs all awaitables concurrently. It will complete when
        # all tasks are finished or when it is cancelled.
        await asyncio.gather(server.serve(), log_writer.run(), flush_timer.run())
    except asyncio.CancelledError:
        # This is the EXPECTED exception when Ctrl+C is pressed.
        # It's not an error, it's the signal to begin a graceful shutdown.
        log.info("Shutdown signal received. Main task has been cancelled.")
    finally:
        # This block is guaranteed to run, ensuring a clean shutdown.
        log.info("--- Starting Graceful Shutdown ---")

        # 1. Stop the flush timer from creating new flush events.
        flush_timer.stop()

        # 2. Stop the log writer, which will finish processing any remaining messages.
        await log_writer.stop()

        # The Uvicorn server's shutdown is handled automatically by the cancellation.
        log.info("--- Telemetry Sink Shut Down Gracefully ---")


if __name__ == "__main__":
    # This is the main entry point for the Python interpreter.
    try:
        # asyncio.run() starts the event loop and runs our main coroutine.
        # It automatically handles KeyboardInterrupt (Ctrl+C) by cancelling
        # the main task, which triggers our graceful shutdown logic.
        asyncio.run(main())
    except KeyboardInterrupt:
        # This catch is optional but prevents the ugly traceback from
        # being printed, making the final exit look clean.
        log.info("Application stopped by user (KeyboardInterrupt).")
