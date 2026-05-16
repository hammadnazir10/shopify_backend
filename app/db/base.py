"""SQLAlchemy engine, session factory, and base class."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Create tables and apply legacy migrations. Idempotent."""
    # Import models to ensure they are registered on the metadata.
    from app.db import models  # noqa: F401
    from app.db.migrations import migrate_ring_design_schema, migrate_user_schema

    Base.metadata.create_all(bind=engine)
    migrate_user_schema()
    migrate_ring_design_schema()
