"""Build structured Incident domain objects from parsed log records."""

from collections import Counter
from typing import Any

from app.models.incident import Incident


class IncidentBuilder:
    """Derive an initial incident record from parsed logs."""

    def build(self, parsed_logs: list[dict[str, Any]]) -> Incident:
        if not parsed_logs:
            raise ValueError("parsed_logs must not be empty")

        services = self._extract_services(parsed_logs)
        severity = self._determine_severity(parsed_logs)
        evidence = self._build_evidence(parsed_logs)

        title = self._build_title(services, severity)
        timestamp = parsed_logs[0].get("timestamp")

        return Incident(
            title=title,
            timestamp=timestamp,
            severity=severity,
            affected_services=services,
            logs=parsed_logs,
            evidence=evidence,
        )

    def _extract_services(self, parsed_logs: list[dict[str, Any]]) -> list[str]:
        services = []
        for log in parsed_logs:
            service = log.get("service")
            if service and service not in services:
                services.append(service)
        return services

    def _determine_severity(self, parsed_logs: list[dict[str, Any]]) -> str:
        levels = Counter(log.get("level", "INFO") for log in parsed_logs)

        if levels.get("ERROR", 0) > 0:
            return "Critical"
        if levels.get("WARNING", 0) > 0:
            return "Medium"
        return "Low"

    def _build_evidence(self, parsed_logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "timestamp": log.get("timestamp"),
                "level": log.get("level"),
                "service": log.get("service"),
                "message": log.get("message"),
            }
            for log in parsed_logs
        ]

    def _build_title(self, services: list[str], severity: str) -> str:
        if services:
            primary_service = services[0]
            return f"{severity} incident affecting {primary_service}"
        return f"{severity} incident"