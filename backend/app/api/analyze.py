from __future__ import annotations

import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.incident_repository import IncidentRepository
from app.services.log_parser import LogParser
from app.services.incident_builder import IncidentBuilder
from app.agents.reasoning_agent import ReasoningAgent
from app.schemas.incident import AnalyzeIncidentResponse, IncidentReport

router = APIRouter(tags=["Incident Analysis"])


@router.post("/analyze", response_model=AnalyzeIncidentResponse)
async def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A log file is required.",
        )

    if not file.filename.lower().endswith((".log", ".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .log and .txt files are supported.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_path = temp_file.name
            temp_file.write(await file.read())

        parser = LogParser()
        logs = parser.parse(temp_path)

        if not logs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No parsable log entries were found. Use lines such as '12:00:01 INFO request routed successfully'.",
            )

        builder = IncidentBuilder()
        incident = builder.build(logs)

        agent = ReasoningAgent()
        incident = agent.analyze(incident)

        repository = IncidentRepository(db)
        repository.save(incident, source_file=file.filename)

        return AnalyzeIncidentResponse(
            incident=IncidentReport(
                incident_id=incident.incident_id,
                title=incident.title,
                timestamp=incident.timestamp,
                created_at=incident.created_at,
                severity=incident.severity,
                root_cause=incident.root_cause,
                confidence=incident.confidence,
                affected_services=incident.affected_services,
                evidence=[
                    {
                        "timestamp": evidence.get("timestamp"),
                        "level": evidence.get("level"),
                        "service": evidence.get("service"),
                        "message": evidence.get("message"),
                    }
                    for evidence in incident.evidence
                ],
                prediction=incident.prediction,
                recommendations=incident.recommendations,
                explanation=incident.explanation,
            ),
            metadata={
                "source_file": file.filename,
                "log_count": len(logs),
            },
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get("/incident/{incident_id}", response_model=IncidentReport)
def get_incident(incident_id: str, db: Session = Depends(get_db)) -> IncidentReport:
    repository = IncidentRepository(db)
    record = repository.get_by_id(incident_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found.",
        )

    incident = repository.to_domain_model(record)
    return IncidentReport(
        incident_id=incident.incident_id,
        title=incident.title,
        timestamp=incident.timestamp,
        created_at=incident.created_at,
        severity=incident.severity,
        root_cause=incident.root_cause,
        confidence=incident.confidence,
        affected_services=incident.affected_services,
        evidence=incident.evidence,
        prediction=incident.prediction,
        recommendations=incident.recommendations,
        explanation=incident.explanation,
    )