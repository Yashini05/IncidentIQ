"""Domain models for IncidentIQ incident analysis."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Incident(BaseModel):
	"""Structured representation of an analyzed incident."""

	incident_id: str = Field(default_factory=lambda: uuid4().hex)
	title: str | None = None
	source_file: str | None = None
	timestamp: str | None = None
	created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
	severity: str | None = None
	root_cause: str | None = None
	confidence: float | None = Field(default=None, ge=0.0, le=100.0)
	affected_services: list[str] = Field(default_factory=list)
	logs: list[dict[str, Any]] = Field(default_factory=list)
	evidence: list[dict[str, Any]] = Field(default_factory=list)
	prediction: str | None = None
	recommendations: list[str] = Field(default_factory=list)
	explanation: str | None = None

