"""Database session dependency for FastAPI routes."""

from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.db.base import SessionLocal


def get_db() -> Iterator[Session]:
    """Yield a SQLAlchemy session and ensure it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
