from sensor_node.services.sensor_service import SensorService
from sensor_node.services.retry_service import RetryService
from sensor_node.infrastructure.http_client import AsyncHttpTelemetryClient
from sensor_node.infrastructure.database.sqlite.repository import SensorDataSQLRepository


def create_sensor_service(name: str, rate: float, endpoint: str):
    client = AsyncHttpTelemetryClient(endpoint=endpoint)
    repo = SensorDataSQLRepository()
    return SensorService(
        sensor_name=name,
        repository=repo,
        rate=rate,
        client=client,
    )


def create_retry_service(
    endpoint: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    check_interval: float = 10.0,
    batch_size: int = 100,
):
    retry_service = RetryService(
        repository=SensorDataSQLRepository(),
        client=AsyncHttpTelemetryClient(endpoint=endpoint),
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        check_interval=check_interval,
        batch_size=batch_size,
    )
    return retry_service
