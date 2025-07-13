import asyncio
import json
import logging
from datetime import datetime
from typing import List

import aiofiles

from telemetry_sink.services.buffer_manager import BufferManager
from telemetry_sink.services.crypto_service import CryptoService
from telemetry_sink.domain.sensor import SensorData

log = logging.getLogger(__name__)


class LogWriter:
    """
    A background service that writes buffered messages to an encrypted log file.
    """

    def __init__(self, buffer_manager: BufferManager, crypto_service: CryptoService, file_path: str):
        self.buffer_manager = buffer_manager
        self.crypto_service = crypto_service
        self.file_path = file_path
        self._stopped = False

    def _default_json_serializer(self, obj):
        """Custom serializer to handle datetime objects for JSON."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    async def _write_batch_to_file(self, batch: List[SensorData]):
        """Encrypts and writes a batch of messages to the log file."""
        if not batch:
            return

        log.info(f"Writing a batch of {len(batch)} messages to {self.file_path}")
        try:
            # Use aiofiles to open the file asynchronously in append-binary mode.
            async with aiofiles.open(self.file_path, "ab") as f:
                for data in batch:
                    json_string = json.dumps(data.to_dict(), default=self._default_json_serializer)

                    plaintext_bytes = json_string.encode("utf-8")

                    # 4. Encrypt the bytes
                    encrypted_bytes = self.crypto_service.encrypt(plaintext_bytes)

                    # 5. Write the encrypted data followed by a newline
                    await f.write(encrypted_bytes + b"\n")

                await f.flush()
        except Exception as e:
            log.error(f"Failed to write batch to log file: {e}", exc_info=True)

    async def run(self):
        """The main execution loop for the log writer."""
        log.info("Log writer service started.")
        while not self._stopped:
            try:
                # Block until the buffer signals a flush is needed.
                await self.buffer_manager.wait_for_flush_event()

                # After waking up, get all messages from the buffer.
                batch = await self.buffer_manager.get_batch()

                if batch:
                    await self._write_batch_to_file(batch)

            except asyncio.CancelledError:
                log.info("Log writer task has been cancelled.")
                break

        # After the loop is stopped, perform one final write for any stragglers.
        log.info("Log writer loop finished, performing final write.")
        final_batch = await self.buffer_manager.get_batch()
        if final_batch:
            await self._write_batch_to_file(final_batch)

        log.info("Log writer has stopped.")

    async def stop(self):
        """Stops the log writer after its current batch is finished."""
        log.info("Stopping log writer...")
        self._stopped = True
        self.buffer_manager.flush()
