import asyncio
import logging
from typing import List

from telemetry_sink.domain.sensor import SensorData

log = logging.getLogger(__name__)


class BufferManager:
    """
    Manages an in-memory buffer for sensor data.

    This class provides an async-safe queue to decouple message reception
    from file writing. It signals a separate writer task when the buffer
    should be flushed.
    """

    def __init__(self, max_size_bytes: int):
        """
        Initializes the BufferManager.

        Args:
            max_size_bytes: The buffer size in bytes that triggers a flush.
        """
        self.max_size_bytes = max_size_bytes
        self._queue = asyncio.Queue()
        self._current_size_bytes = 0

        # Event to signal the LogWriter that a flush is needed
        self._flush_event = asyncio.Event()

        # Lock to protect access to the size counter
        self._lock = asyncio.Lock()

    async def add(self, data: SensorData, size_bytes: int):
        """
        Adds a new message to the buffer.

        If adding the message causes the buffer to exceed its max size,
        it will trigger a flush event.
        """
        await self._queue.put(data)

        async with self._lock:
            self._current_size_bytes += size_bytes
            if self._current_size_bytes >= self.max_size_bytes:
                log.info(f"Buffer size {self._current_size_bytes} >= max {self.max_size_bytes}. Triggering flush.")
                self.flush()

    def flush(self):
        """
        Manually trigger a flush event.

        This is called by the FlushTimer or when the buffer is full.
        It is a non-blocking operation.
        """
        self._flush_event.set()

    async def wait_for_flush_event(self):
        """
        Waits until a flush is signaled, then resets the event.

        This is the primary entry point for the LogWriter's loop.
        """
        await self._flush_event.wait()
        self._flush_event.clear()

    async def get_batch(self) -> List[SensorData]:
        """
        Atomically drains the queue and returns all items as a batch.

        This also resets the internal byte counter.
        """
        batch = []
        if self._queue.empty():
            return batch

        async with self._lock:
            while not self._queue.empty():
                try:
                    item = self._queue.get_nowait()
                    batch.append(item)
                except asyncio.QueueEmpty:
                    # This should not happen due to the lock, but is safe to handle
                    break

            # Reset the size counter after draining the queue
            self._current_size_bytes = 0

        log.debug(f"Drained {len(batch)} items from buffer.")
        return batch
