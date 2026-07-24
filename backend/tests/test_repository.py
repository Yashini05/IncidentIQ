from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.models.incident import Incident
from app.models.incident_record import IncidentRecord
from app.repositories.incident_repository import IncidentRepository


def test_incident_repository_persists_and_loads_incident(tmp_path):
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'incidents.db'}")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with session_factory() as session:
        repository = IncidentRepository(session)
        incident = Incident(
            title="Critical incident affecting Database",
            timestamp="12:00:05",
            created_at=datetime.now(timezone.utc),
            severity="Critical",
            root_cause="Database Failure",
            confidence=96.0,
            affected_services=["Database", "Payment"],
            logs=[],
            evidence=[{"timestamp": "12:00:05", "level": "ERROR", "service": "Database", "message": "database connection pool exhausted"}],
            prediction="Downstream write and read paths may fail across dependent services.",
            recommendations=["Check database availability."],
            explanation="Root cause assessment: Database Failure.",
        )

        saved = repository.save(incident, source_file="incident.log")
        loaded = repository.get_by_id(saved.incident_id)

        assert loaded is not None
        assert loaded.incident_id == incident.incident_id
        assert loaded.source_file == "incident.log"
        assert loaded.root_cause == "Database Failure"
        assert loaded.affected_services == ["Database", "Payment"]

        domain = repository.to_domain_model(loaded)
        assert domain.incident_id == incident.incident_id
        assert domain.recommendations == ["Check database availability."]
