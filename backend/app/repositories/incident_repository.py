"""Incident persistence operations for IncidentIQ."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.incident_record import IncidentRecord


class IncidentRepository:
    """Persist and retrieve incident analysis results."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, incident: Incident, source_file: str | None = None) -> IncidentRecord:
        """Insert or update an incident record."""

        record = self._session.get(IncidentRecord, incident.incident_id)
        if record is None:
            record = IncidentRecord(incident_id=incident.incident_id)

        record.title = incident.title
        record.source_file = source_file or incident.source_file
        record.timestamp = incident.timestamp
        record.created_at = incident.created_at
        record.severity = incident.severity
        record.root_cause = incident.root_cause
        record.confidence = incident.confidence
        record.affected_services = incident.affected_services
        record.evidence = incident.evidence
        record.prediction = incident.prediction
        record.recommendations = incident.recommendations
        record.explanation = incident.explanation

        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return record

    def get_by_id(self, incident_id: str) -> IncidentRecord | None:
        """Fetch a persisted incident by identifier."""

        return self._session.get(IncidentRecord, incident_id)

    @staticmethod
    def to_domain_model(record: IncidentRecord) -> Incident:
        """Convert a persisted record back into the domain incident model."""

        return Incident(
            incident_id=record.incident_id,
            title=record.title,
            source_file=record.source_file,
            timestamp=record.timestamp,
            created_at=record.created_at,
            severity=record.severity,
            root_cause=record.root_cause,
            confidence=record.confidence,
            affected_services=list(record.affected_services or []),
            logs=[],
            evidence=[_normalize_evidence(item) for item in record.evidence or []],
            prediction=record.prediction,
            recommendations=list(record.recommendations or []),
            explanation=record.explanation,
        )


def _normalize_evidence(item: dict[str, Any]) -> dict[str, Any]:
    """Keep evidence dictionaries JSON serializable and predictable."""

    return {
        "timestamp": item.get("timestamp"),
        "level": item.get("level"),
        "service": item.get("service"),
        "message": item.get("message"),
    }
