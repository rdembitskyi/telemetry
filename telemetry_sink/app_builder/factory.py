import logging
from configparser import ConfigParser
import uvicorn

from telemetry_sink.services.rate_limiter import RateLimiter
from telemetry_sink.services.crypto_service import CryptoService
from telemetry_sink.services.buffer_manager import BufferManager
from telemetry_sink.services.log_writer import LogWriter
from telemetry_sink.services.flush_timer import FlushTimer
from telemetry_sink.services.telemetry_service import TelemetryService

# Import the adapter factory
from telemetry_sink.adapters.http_server import create_http_api_app

log = logging.getLogger(__name__)


def create_rate_limiter(config: ConfigParser) -> RateLimiter:
    """Creates a RateLimiter instance from configuration."""
    log.info("Creating Rate Limiter service...")
    rate = config.getint("telemetry_sink_rate_limit", "limit_bytes_per_sec", fallback=5242880)
    capacity = config.getint("telemetry_sink_rate_limit", "capacity_bytes", fallback=5242880)
    log.info(f"-> Rate Limiter configured with rate={rate} B/s, capacity={capacity} B")
    return RateLimiter(rate_limit_bytes_per_sec=rate)


def create_crypto_service(config: ConfigParser) -> CryptoService:
    """Creates a CryptoService instance from configuration."""
    log.info("Creating Crypto service...")
    # No fallback for the key - the application should fail if it's missing.
    try:
        key = config.get("telemetry_sink_logging", "encryption_key")
        return CryptoService(key)
    except Exception as e:
        log.critical(f"FATAL: Could not create CryptoService. Check 'encryption_key' in config.ini. Error: {e}")
        raise


def create_buffer_manager(config: ConfigParser) -> BufferManager:
    """Creates a BufferManager instance from configuration."""
    log.info("Creating Buffer Manager service...")
    max_size = config.getint("buffer", "size_bytes", fallback=1048576)
    log.info(f"-> Buffer Manager configured with max_size={max_size} bytes")
    return BufferManager(max_size_bytes=max_size)


def create_log_writer(config: ConfigParser, buffer_manager: BufferManager, crypto_service: CryptoService) -> LogWriter:
    """Creates a LogWriter instance, injecting its dependencies."""
    log.info("Creating Log Writer service...")
    file_path = config.get("logging", "file_path", fallback="./telemetry.log.enc")
    log.info(f"-> Log Writer configured to write to '{file_path}'")
    return LogWriter(buffer_manager=buffer_manager, crypto_service=crypto_service, file_path=file_path)


def create_flush_timer(config: ConfigParser, buffer_manager: BufferManager) -> FlushTimer:
    """Creates a FlushTimer instance, injecting its dependency."""
    log.info("Creating Flush Timer service...")
    interval = config.getfloat("buffer", "flush_interval", fallback=0.1)
    log.info(f"-> Flush Timer configured with interval={interval}s")
    return FlushTimer(buffer_manager=buffer_manager, interval=interval)


def create_telemetry_service(config: ConfigParser) -> TelemetryService:
    """
    Creates and wires up the core application services.

    This acts as a master factory for the application's core logic,
    creating the shared dependencies that other services will use.
    """
    log.info("Wiring up core application services...")
    # Create the shared, independent services first
    rate_limiter = create_rate_limiter(config)
    buffer_manager = create_buffer_manager(config)

    # Create the main service and inject its dependencies
    telemetry_service = TelemetryService(rate_limiter=rate_limiter, buffer_manager=buffer_manager)
    return telemetry_service


def create_api_app(telemetry_service: TelemetryService, host: str, port: int, server_protocol: str = "http"):
    """Creates the FastAPI application, injecting the core telemetry service."""
    log.info("Creating FastAPI adapter...")
    if server_protocol == "http":
        app = create_http_api_app(telemetry_service)
        # Configure the Uvicorn server to be managed by our asyncio loop
        server_config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="info",
        )
        return uvicorn.Server(server_config)
    else:
        raise ValueError(f"Unsupported server protocol: {server_protocol}. Only 'http' is supported at this time.")
