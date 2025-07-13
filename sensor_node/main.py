import asyncio
import logging
from sensor_node.app_builder.config import load_config
from sensor_node.app_builder.factory import create_sensor_service, create_retry_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - [%(taskName)s] - %(message)s")
log = logging.getLogger(__name__)


async def main():
    """
    The main asynchronous entry point for the application.
    Sets up and runs services, and handles graceful shutdown.
    """
    log.info("Application starting up...")

    # 1) Initialize services and resources
    config = load_config()
    sensor_name = config.get("sensor", "name", fallback="default_sensor")
    sensor_rate = config.getfloat("sensor", "rate", fallback=1.0)
    sink_endpoint = config.get("telemetry_sink", "endpoint", fallback="http://localhost:8000/telemetry")

    sensor_service = create_sensor_service(name=sensor_name, rate=sensor_rate, endpoint=sink_endpoint)
    retry_service = create_retry_service(endpoint=sink_endpoint)

    # 2) Create the tasks to run concurrently
    tasks = {
        asyncio.create_task(sensor_service.start(), name="SensorService"),
        asyncio.create_task(retry_service.start(), name="RetryService"),
    }
    log.info("Services have been started as concurrent tasks.")

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        log.info("Shutdown signal received. Main task cancelled.")
    finally:
        log.info("Starting graceful shutdown of all resources...")

        await sensor_service.stop()
        await retry_service.stop()

        log.info("All resources have been shut down gracefully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Application stopped by user (KeyboardInterrupt).")
