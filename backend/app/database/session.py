"""Database session configuration for IncidentIQ."""

from __future__ import annotations

import os
from functools import lru_cache
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def _get_database_url() -> str:
    """Return the configured database URL.

    The application prefers DATABASE_URL from the environment. For local
    development, fall back to a SQLite database stored in the backend folder
    so the service can start without any extra configuration.
    """

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        database_path = Path(__file__).resolve().parents[3] / "incidentiq.db"
        database_url = f"sqlite+pysqlite:///{database_path.as_posix()}"
    return database_url


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


@lru_cache(maxsize=1)
def get_engine():
    """Create a SQLAlchemy engine using the configured database URL."""

    return create_engine(_get_database_url(), pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Create a SQLAlchemy session factory."""

    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for dependency injection."""

    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
