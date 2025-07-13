import asyncio
import logging

from telemetry_sink.services.buffer_manager import BufferManager

log = logging.getLogger(__name__)


class FlushTimer:
    """
    A simple background service that periodically triggers a buffer flush.
    """

    def __init__(self, buffer_manager: BufferManager, interval: float):
        """
        Initializes the FlushTimer.

        Args:
            buffer_manager: The buffer manager instance to signal.
            interval: The flush interval in seconds.
        """
        self.buffer_manager = buffer_manager
        self.interval = interval
        self._stopped = False

    async def run(self):
        """
        The main execution loop for the timer.

        This should be run as a background asyncio task.
        """
        log.info(f"Flush timer started with a {self.interval}s interval.")
        while not self._stopped:
            try:
                # Wait for the specified interval.
                await asyncio.sleep(self.interval)

                # Check if stop was called during the sleep.
                if self._stopped:
                    break

                log.debug("Timer triggered. Signaling buffer flush.")
                self.buffer_manager.flush()

            except asyncio.CancelledError:
                # This is raised when the task is cancelled by the orchestrator.
                log.info("Flush timer task has been cancelled.")
                break

        log.info("Flush timer has stopped.")

    def stop(self):
        """Stops the timer's execution loop."""
        log.info("Stopping flush timer...")
        self._stopped = True
