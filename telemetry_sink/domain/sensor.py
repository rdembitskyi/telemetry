from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SensorData:
    name: str
    value: int
    timestamp: datetime

    def to_dict(self) -> dict:
        """
        Convert the SensorData instance to a dictionary.

        Returns:
            dict: A dictionary representation of the SensorData instance.
        """
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
        }
