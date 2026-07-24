import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.database import session as db_session
from main import app


def test_analyze_and_fetch_incident_round_trip(tmp_path, monkeypatch):
    db_path = tmp_path / "incidentiq.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_path}")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    db_session.get_engine.cache_clear()
    db_session.get_session_factory.cache_clear()

    log_file = tmp_path / "incident.log"
    log_file.write_text(
        "12:00:01 INFO request routed successfully\n"
        "12:00:05 ERROR database connection pool exhausted\n"
        "12:00:07 ERROR payment request timed out after dependency failure\n",
        encoding="utf-8",
    )

    with TestClient(app) as client:
        with log_file.open("rb") as handle:
            response = client.post("/analyze", files={"file": (log_file.name, handle, "text/plain")})

        assert response.status_code == 200
        payload = response.json()
        incident = payload["incident"]

        assert incident["severity"] == "Critical"
        assert incident["root_cause"] == "Database Failure"
        assert incident["confidence"] is not None

        incident_id = incident["incident_id"]
        fetch_response = client.get(f"/incident/{incident_id}")
        assert fetch_response.status_code == 200
        fetched = fetch_response.json()
        assert fetched["incident_id"] == incident_id
        assert fetched["root_cause"] == "Database Failure"


def test_analyze_rejects_unparsable_logs(tmp_path, monkeypatch):
    db_path = tmp_path / "incidentiq.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_path}")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    db_session.get_engine.cache_clear()
    db_session.get_session_factory.cache_clear()

    log_file = tmp_path / "broken.log"
    log_file.write_text("this line does not match the parser\n", encoding="utf-8")

    with TestClient(app) as client:
        with log_file.open("rb") as handle:
            response = client.post("/analyze", files={"file": (log_file.name, handle, "text/plain")})

        assert response.status_code == 400
        assert response.json()["detail"].startswith("No parsable log entries")
