from typing import List, Optional
from uuid import UUID

from sensor_node.domain.interfaces import SensorDataRepository
from sensor_node.domain.sensor import SensorData, SensorDataDeliveryStatus
from sensor_node.infrastructure.database.sqlite.models import SensorDataModel
from sensor_node.infrastructure.database.sqlite.connect import get_db_session
from sqlalchemy import update
from sensor_node.infrastructure.database.exceptions import RecordNotFoundError


class SensorDataSQLRepository(SensorDataRepository):
    """
    Synchronous repository for SensorDataModel using SQLAlchemy with SQLite.

    I used SQLITE and synchronous SQLAlchemy for simplicity and ease of setup.
    In production, you might want to use an asynchronous database driver like asyncpg
    Depending on application load we might consider NoSQL databases for better performance.
    """

    def __init__(self, session_factory=get_db_session):
        """
        :param session_factory: a context‐manager callable yielding a SQLAlchemy Session
        """
        self._session_factory = session_factory

    def create(self, sensor_data: SensorData) -> SensorData:
        """
        Persist a new SensorData record and return the saved domain object
        """
        with self._session_factory() as session:
            orm = SensorDataModel.from_domain(sensor_data)
            session.add(orm)
            session.commit()
            session.refresh(orm)
            return orm.to_domain()

    def update_status(self, object_id: UUID, status: SensorDataDeliveryStatus) -> bool:
        """
        Atomically update only the `status` field of an existing SensorData record
        """
        with self._session_factory() as session:
            stmt = (
                update(SensorDataModel)
                .where(SensorDataModel.id == object_id)
                .values(status=status)
                .execution_options(synchronize_session="fetch")
            )
            result = session.execute(stmt)
            if result.rowcount == 0:
                raise RecordNotFoundError(f"SensorData with id {object_id} not found")

            session.commit()
            return True

    def update_retry_count(self, object_id: UUID, retry_count: int) -> bool:
        """
        Atomically update only the `status` field of an existing SensorData record
        """
        with self._session_factory() as session:
            stmt = (
                update(SensorDataModel)
                .where(SensorDataModel.id == object_id)
                .values(retry_count=retry_count)
                .execution_options(synchronize_session="fetch")
            )
            result = session.execute(stmt)
            if result.rowcount == 0:
                raise RecordNotFoundError(f"SensorData with id {object_id} not found")

            session.commit()
            return True

    def list_by_status(self, status: SensorDataDeliveryStatus, batch_size: int) -> List[SensorData]:
        """
        Return all sensor readings matching a given status.
        """
        with self._session_factory() as session:
            orm_list = session.query(SensorDataModel).filter_by(status=status).limit(batch_size).all()
            return [o.to_domain() for o in orm_list]
