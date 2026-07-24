"""SQLAlchemy ORM model for persisted IncidentIQ incidents."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class IncidentRecord(Base):
    """Persisted incident analysis record."""

    __tablename__ = "incidents"

    incident_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    severity: Mapped[str | None] = mapped_column(String(32), nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    affected_services: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    evidence: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    prediction: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
