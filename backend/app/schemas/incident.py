"""Pydantic schemas for IncidentIQ incident analysis APIs."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IncidentEvidence(BaseModel):
    """Single evidence item extracted from log content."""

    timestamp: str | None = None
    level: str | None = None
    service: str | None = None
    message: str | None = None


class IncidentReport(BaseModel):
    """Structured incident payload returned by the analysis pipeline."""

    incident_id: str
    title: str | None = None
    timestamp: str | None = None
    created_at: datetime
    severity: str | None = None
    root_cause: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=100.0)
    affected_services: list[str] = Field(default_factory=list)
    evidence: list[IncidentEvidence] = Field(default_factory=list)
    prediction: str | None = None
    recommendations: list[str] = Field(default_factory=list)
    explanation: str | None = None


class AnalyzeIncidentResponse(BaseModel):
    """API response envelope for the /analyze endpoint."""

    incident: IncidentReport
    metadata: dict[str, Any] = Field(default_factory=dict)
