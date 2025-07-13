import aiohttp
from sensor_node.domain.interfaces import TelemetryClient
from sensor_node.domain.sensor import SensorData


class AsyncHttpTelemetryClient(TelemetryClient):
    def __init__(self, endpoint: str, timeout: float = 5.0):
        self.endpoint = endpoint
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = aiohttp.ClientSession(timeout=self._timeout)

    async def send(self, sensor_data: SensorData) -> None:
        payload = {
            "name": sensor_data.name,
            "value": sensor_data.value,
            "timestamp": int(sensor_data.timestamp.timestamp() * 1000),
        }
        async with self._session.post(url=self.endpoint, json=payload) as resp:
            resp.raise_for_status()

    async def close(self) -> None:
        await self._session.close()
