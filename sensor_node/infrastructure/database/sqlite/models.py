import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, UUID, Index
from sqlalchemy.orm import declarative_base

from sensor_node.domain.sensor import SensorDataDeliveryStatus
from sensor_node.domain.sensor import SensorData

Base = declarative_base()


class SensorDataModel(Base):
    __tablename__ = "sensor_data"
    __table_args__ = (
        Index("ix_sensor_data_status", "status"),
        Index("ix_sensor_data_name", "name"),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(length=100), nullable=False)
    value = Column(Integer, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    status = Column(
        SQLEnum(SensorDataDeliveryStatus, name="sensor_status"),
        nullable=False,
        default=SensorDataDeliveryStatus.PENDING,
    )
    retry_count = Column(Integer, nullable=False, default=0)

    def to_domain(self) -> "SensorData":
        """
        Convert this ORM object back into your domain dataclass.
        """

        return SensorData(
            id=self.id,
            name=self.name,
            value=self.value,
            timestamp=self.timestamp,
            status=self.status,
        )

    @staticmethod
    def from_domain(sensor_data: SensorData) -> "SensorDataModel":
        """
        Convert a domain dataclass into this ORM object.
        """
        return SensorDataModel(
            id=sensor_data.id,
            name=sensor_data.name,
            value=sensor_data.value,
            timestamp=sensor_data.timestamp,
            status=sensor_data.status,
        )
