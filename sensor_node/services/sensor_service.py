import asyncio
import random
import uuid
import logging
from datetime import datetime
from sensor_node.domain.sensor import SensorData, SensorDataDeliveryStatus
from sensor_node.domain.interfaces import TelemetryClient, SensorDataRepository


logger = logging.getLogger(__name__)


class SensorService:
    def __init__(
        self,
        client: TelemetryClient,
        repository: SensorDataRepository,
        sensor_name: str,
        rate: float,
    ):
        self.client = client
        self.repository = repository
        self.sensor_name = sensor_name
        self.interval = 1.0 / rate
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        try:
            while not self._stop_event.is_set():
                data = self.create_sensor_data()
                try:
                    logger.info(f"Sending message: {data.id} for sensor '{self.sensor_name}'")
                    await self.client.send(data)
                    self.repository.update_status(object_id=data.id, status=SensorDataDeliveryStatus.DElIVERED)
                    logger.info(f"DELIVERED message: {data.id} for sensor '{self.sensor_name}'")
                except Exception:
                    logger.error(f"Failed to send message: {data.id} for sensor '{self.sensor_name}'")
                    # Update status to FAILED in the repository
                    # This will allow the retry service to pick it up later
                    self.repository.update_status(object_id=data.id, status=SensorDataDeliveryStatus.FAILED)
                await asyncio.sleep(self.interval)
        finally:
            await self.client.close()

    def create_sensor_data(self) -> SensorData:
        """
        Generate a mock sensor data object with a random value and current timestamp.
        Saves the data to the database.

        Returns:
            SensorData: A SensorData object with the given name, a random value, and the current timestamp.
        """

        data = SensorData(
            id=uuid.uuid4(),
            name=self.sensor_name,
            value=random.randint(0, 100),
            timestamp=datetime.utcnow(),
            status=SensorDataDeliveryStatus.PENDING,
        )
        self.repository.create(data)

        return data

    async def stop(self) -> None:
        logger.info(f"Stopping sensor service for '{self.sensor_name}'")
        self._stop_event.set()
        await self.client.close()
