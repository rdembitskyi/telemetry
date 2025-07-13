import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SensorDataDeliveryStatus(Enum):
    DElIVERED = "DELIVERED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    PERMANENT_FAILURE = "PERMANENT_FAILURE"
    RETRYING = "RETRYING"


@dataclass(frozen=True)
class SensorData:
    id: uuid.UUID
    name: str
    value: int
    timestamp: datetime
    status: SensorDataDeliveryStatus = SensorDataDeliveryStatus.PENDING
    retry_count: int = 0
