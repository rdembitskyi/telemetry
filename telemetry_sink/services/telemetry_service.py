import logging
from telemetry_sink.services.rate_limiter import RateLimiter, RateLimitExceededError
from telemetry_sink.services.buffer_manager import BufferManager
from telemetry_sink.domain.sensor import SensorData

log = logging.getLogger(__name__)


class TelemetryService:
    """The central application service that orchestrates core logic."""

    def __init__(self, rate_limiter: RateLimiter, buffer_manager: BufferManager):
        self.rate_limiter = rate_limiter
        self.buffer_manager = buffer_manager

    async def process_message(self, data: SensorData, size_bytes: int):
        """
        The single, protocol-agnostic entry point for processing a message.

        Raises:
            RateLimitExceededError: If the incoming data violates the rate limit.
        """
        # 1. Check Rate Limiter
        if not await self.rate_limiter.check(size_bytes):
            raise RateLimitExceededError(f"Rate limit exceeded for {size_bytes} bytes")

        # 2. Add to Buffer (this is an async operation)
        await self.buffer_manager.add(data, size_bytes)
        log.debug(f"Message from sensor '{data.name}' accepted into buffer.")
