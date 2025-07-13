import asyncio
import logging
import random
from typing import Optional


from sensor_node.domain.interfaces import SensorDataRepository, TelemetryClient
from sensor_node.domain.sensor import SensorDataDeliveryStatus, SensorData


class RetryService:
    """
    Service responsible for retrying failed sensor data transmissions.

    Implements an exponential backoff strategy and limits the number of retries.
    """

    def __init__(
        self,
        repository: SensorDataRepository,
        client: TelemetryClient,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        check_interval: float = 30.0,
        batch_size: int = 100,
    ):
        """
        Initialize the retry service.

        Args:
            repository: Repository for accessing sensor data
            client: Client for sending telemetry data
            max_retries: Maximum number of retry attempts per record
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            check_interval: Time between checking for failed records in seconds
        """
        self.repository = repository
        self.client = client
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.check_interval = check_interval
        self.batch_size = batch_size
        self._stop_event = asyncio.Event()
        self._task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(__name__)

    async def start(self):
        """Start the retry service."""
        self._stop_event.clear()
        self._task = asyncio.create_task(self._retry_loop())
        self.logger.info("RetryService started")

    async def wait_until_stopped(self):
        """Wait until the service is stopped and its tasks are done."""
        if self._task:
            await self._task

    async def stop(self):
        """Stop the retry service."""
        if not self._stop_event.is_set():
            self._stop_event.set()
            await self.client.close()
            self.logger.info("RetryService stopping")

    async def _retry_loop(self):
        """Main retry loop that periodically checks for failed records."""
        while not self._stop_event.is_set():
            try:
                await self._process_failed_records()
            except Exception as e:
                self.logger.error(f"Error in retry loop: {e}")

            try:
                # Wait for the next check interval or until stop is called
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.check_interval)
            except asyncio.TimeoutError:
                # This is expected when the timeout occurs
                pass

        self.logger.info("RetryService stopped")

    async def _process_failed_records(self):
        """Process all records that need to be retried."""
        # Get all records with FAILED status

        # For simplicity, I select all failed records in batches
        # And send them one by one
        # In a real-world scenario, you might want to use a more sophisticated strategy
        # to handle large volumes of data, such as using a queue or stream processing.
        failed_records = self.repository.list_by_status(
            status=SensorDataDeliveryStatus.FAILED, batch_size=self.batch_size
        )

        if not failed_records:
            return

        self.logger.info(f"Processing {len(failed_records)} failed records")

        for record in failed_records:
            await self.retry_record(record)

    async def retry_record(self, record: SensorData):
        """Retry sending a single failed record with backoff."""
        if self._stop_event.is_set():
            self.logger.info("RetryService is stopping, skipping retries")
            return

        if record.retry_count >= self.max_retries:
            # Mark as permanently failed if max retries reached
            self.repository.update_status(object_id=record.id, status=SensorDataDeliveryStatus.PERMANENT_FAILURE)
            self.logger.warning(f"Record {record.id} permanently failed after {record.retry_count} retries")
            return

        self.repository.update_status(object_id=record.id, status=SensorDataDeliveryStatus.RETRYING)

        # Calculate backoff delay based on retry count
        delay = min(self.initial_delay * (2**record.retry_count) * (0.5 + random.random()), self.max_delay)

        self.logger.debug(f"Retrying record {record.id} with delay {delay:.2f}s (attempt {record.retry_count + 1})")

        # Wait for the calculated delay
        await asyncio.sleep(delay)

        try:
            # Attempt to send the data
            await self.client.send(record)
            self.repository.update_status(object_id=record.id, status=SensorDataDeliveryStatus.DElIVERED)
            self.logger.info(f"Successfully retried record {record.id}")

        except Exception as e:
            # Increment retry count and keep FAILED status
            self.repository.update_retry_count(object_id=record.id, retry_count=record.retry_count + 1)
            self.logger.warning(f"Failed to retry record {record.id}: {e}")
