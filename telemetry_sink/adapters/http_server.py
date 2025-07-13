import logging
from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from telemetry_sink.services.telemetry_service import TelemetryService
from telemetry_sink.services.rate_limiter import RateLimitExceededError
from telemetry_sink.domain.sensor import SensorData

logging = logging.getLogger(__name__)


class SensorDataModel(BaseModel):
    name: str
    value: int
    timestamp: datetime


def create_http_api_app(telemetry_service: TelemetryService) -> FastAPI:
    """Factory to create the FastAPI application and its endpoints."""
    app = FastAPI(title="Telemetry Sink")

    @app.post("/telemetry", status_code=status.HTTP_202_ACCEPTED)
    async def receive_telemetry(data: SensorDataModel, request: Request):
        # The 'Content-Length' header gives us the size in bytes.
        try:
            size_bytes = int(request.headers["content-length"])
        except (KeyError, ValueError):
            raise HTTPException(status_code=400, detail="Content-Length header is missing or invalid")

        # Convert the protocol-specific model (Pydantic) to our internal domain model
        domain_data = SensorData(name=data.name, value=data.value, timestamp=data.timestamp)

        try:
            # Call the protocol-agnostic application core
            await telemetry_service.process_message(domain_data, size_bytes)
        except RateLimitExceededError as e:
            logging.warning(f"Throttling request: {e}")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
        except Exception as e:
            logging.error(f"Internal server error while processing message: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

        return {"status": "accepted"}

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app
