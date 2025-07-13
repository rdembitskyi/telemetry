import asyncio
import time
import logging

log = logging.getLogger(__name__)


class RateLimitExceededError(Exception):
    """Custom exception for when the rate limit is exceeded."""

    pass


class RateLimiter:
    """
    An asynchronous Fixed-Interval Rate Limiter.

    This class enforces a strict 'bytes per second' limit. It provides a budget
    of bytes that resets at the beginning of each 1-second window.
    It is async-safe.
    """

    def __init__(self, rate_limit_bytes_per_sec: int):
        """
        Initializes the RateLimiter.

        Args:
            rate_limit_bytes_per_sec: The total budget of bytes allowed per second.
        """
        if rate_limit_bytes_per_sec <= 0:
            raise ValueError("'rate_limit_bytes_per_sec' must be a positive value.")

        self.rate_limit = float(rate_limit_bytes_per_sec)

        # Lock to ensure atomic operations on the counter and timestamp.
        self._lock = asyncio.Lock()

        # Tracks how many bytes have been used in the current window.
        self._bytes_in_window = 0

        # The timestamp when the current 1-second window started.
        self._window_start_time = time.monotonic()

    async def check(self, size_bytes: int) -> bool:
        """
        Checks if a request of a given size can proceed within the current second.

        Args:
            size_bytes: The number of bytes the request costs.

        Returns:
            True if the request is allowed, False otherwise.
        """
        async with self._lock:
            now = time.monotonic()

            # If more than 1 second has passed since the window started, reset it.
            if now >= self._window_start_time + 1.0:
                self._window_start_time = now
                self._bytes_in_window = 0

            # --- Check if the budget for the current window is exceeded ---
            if self._bytes_in_window + size_bytes > self.rate_limit:
                # Reject the request. Not enough budget left in this second.
                return False

            # --- Accept the request and update the counter ---
            self._bytes_in_window += size_bytes
            return True
