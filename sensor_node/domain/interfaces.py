from abc import ABC, abstractmethod
from uuid import UUID

from sensor_node.domain.sensor import SensorData, SensorDataDeliveryStatus


class TelemetryClient(ABC):
    @abstractmethod
    async def send(self, sensor_data: SensorData) -> None:
        """Send a SensorValue to the remote sink via chosen protocol."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the connection to the telemetry sink."""
        pass


class SensorDataRepository(ABC):
    """
    Domain‐layer repository interface for persisting and retrieving SensorData.
    """

    @abstractmethod
    def create(self, sensor_data: SensorData) -> SensorData:
        """
        Persist a new SensorData record and return the saved domain object.
        """
        ...

    @abstractmethod
    def update_status(self, object_id: UUID, status: SensorDataDeliveryStatus) -> SensorData:
        """
        Update the status of an existing SensorData record and return the updated object.
        """
        ...

    @abstractmethod
    def update_retry_count(self, object_id: UUID, retry_count: int) -> bool: ...

    @abstractmethod
    def list_by_status(self, status: SensorDataDeliveryStatus, batch_size: int) -> list[SensorData]:
        """
        Return all sensor readings matching a given status.
        """
        ...
