from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sensor_node.infrastructure.database.sqlite.models import Base

# 1. SQLite engine (file-based)
engine = create_engine(
    "sqlite:///sensor_data.db",
    connect_args={"check_same_thread": False},
    echo=False,
)

# 2. Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db():
    """Create tables based on ORM models."""
    Base.metadata.create_all(bind=engine)


init_db()


@contextmanager
def get_db_session():
    """Yield a SQLAlchemy session and ensure closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
