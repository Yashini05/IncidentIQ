from app.agents.reasoning_agent import ReasoningAgent
from app.services.incident_builder import IncidentBuilder


def test_incident_builder_and_reasoning_identify_database_failure():
    parsed_logs = [
        {
            "timestamp": "12:00:01",
            "level": "INFO",
            "service": "API Gateway",
            "message": "request routed successfully",
        },
        {
            "timestamp": "12:00:05",
            "level": "ERROR",
            "service": "Database",
            "message": "database connection pool exhausted",
        },
        {
            "timestamp": "12:00:07",
            "level": "ERROR",
            "service": "Payment",
            "message": "payment request timed out after dependency failure",
        },
    ]

    incident = IncidentBuilder().build(parsed_logs)
    analyzed = ReasoningAgent().analyze(incident)

    assert analyzed.severity == "Critical"
    assert analyzed.root_cause == "Database Failure"
    assert analyzed.confidence is not None and analyzed.confidence > 90
    assert "Database" in analyzed.affected_services
    assert analyzed.recommendations
    assert analyzed.explanation
