"""Reason over incident evidence and produce an explainable analysis."""

import logging
from collections import Counter
from typing import Any

from app.models.incident import Incident


logger = logging.getLogger(__name__)


class ReasoningAgent:
    """Derive root cause, impact, and response guidance from incident evidence."""

    def analyze(self, incident: Incident) -> Incident:
        if not incident.logs:
            raise ValueError("incident.logs must not be empty")

        services = self._unique_services(incident.logs)
        incident.affected_services = services

        root_cause, evidence, confidence = self._infer_root_cause(incident.logs)
        prediction = self._predict_cascade(services, root_cause)
        recommendations = self._recommendations(root_cause, services, incident.severity)
        explanation = self._build_explanation(root_cause, evidence, prediction, recommendations)

        incident.root_cause = root_cause
        incident.evidence = evidence
        incident.confidence = confidence
        incident.prediction = prediction
        incident.recommendations = recommendations
        incident.explanation = explanation

        logger.info(
            "Incident analyzed",
            extra={
                "incident_id": incident.incident_id,
                "root_cause": root_cause,
                "confidence": confidence,
                "services": services,
            },
        )

        return incident

    def _unique_services(self, logs: list[dict[str, Any]]) -> list[str]:
        services: list[str] = []
        for log in logs:
            service = log.get("service")
            if service and service not in services:
                services.append(service)
        return services

    def _infer_root_cause(self, logs: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]], float]:
        ordered_candidates = [
            ("Database Failure", ["database", "db", "connection pool", "timeout acquiring connection"], 92.0),
            ("Payment Service Failure", ["payment", "checkout", "billing", "charge"], 88.0),
            ("Cache Failure", ["redis", "cache", "cache miss", "unavailable"], 84.0),
            ("Gateway Failure", ["gateway", "api gateway", "edge", "routing"], 80.0),
        ]

        evidence: list[dict[str, Any]] = []
        best_root_cause = "Unclassified Failure"
        best_confidence = 55.0

        for root_cause, keywords, confidence in ordered_candidates:
            matched = self._find_keyword_matches(logs, keywords)
            if matched:
                evidence = matched
                best_root_cause = root_cause
                best_confidence = confidence + min(8.0, len(matched) * 2.0)
                break

        if not evidence:
            error_logs = [log for log in logs if log.get("level") == "ERROR"]
            if error_logs:
                evidence = [
                    {
                        "timestamp": log.get("timestamp"),
                        "level": log.get("level"),
                        "service": log.get("service"),
                        "message": log.get("message"),
                    }
                    for log in error_logs[:3]
                ]
                best_root_cause = "Service Failure Detected"
                best_confidence = 70.0

        return best_root_cause, evidence, min(best_confidence, 99.0)

    def _find_keyword_matches(
        self,
        logs: list[dict[str, Any]],
        keywords: list[str],
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for log in logs:
            message = str(log.get("message", "")).lower()
            if any(keyword in message for keyword in keywords):
                matches.append(
                    {
                        "timestamp": log.get("timestamp"),
                        "level": log.get("level"),
                        "service": log.get("service"),
                        "message": log.get("message"),
                    }
                )
        return matches

    def _predict_cascade(self, services: list[str], root_cause: str) -> str:
        service_count = len(services)

        if root_cause == "Database Failure":
            return "Downstream write and read paths may fail across dependent services."
        if root_cause == "Payment Service Failure":
            return "Transaction workflows may degrade and queue backlogs may increase."
        if root_cause == "Cache Failure":
            return "Increased latency and elevated load on primary persistence layers are likely."
        if root_cause == "Gateway Failure":
            return "Ingress traffic may be blocked or partially routed, impacting multiple services."

        if service_count > 3:
            return "Multiple services are involved, so a cascading dependency issue is possible."
        return "No strong cascade signal is present, but the service should be monitored for recurrence."

    def _recommendations(
        self,
        root_cause: str,
        services: list[str],
        severity: str | None,
    ) -> list[str]:
        recommendations: list[str] = []

        if root_cause == "Database Failure":
            recommendations.extend([
                "Check database availability, connection saturation, and slow queries.",
                "Validate recent schema, failover, or network changes affecting persistence.",
            ])
        elif root_cause == "Payment Service Failure":
            recommendations.extend([
                "Inspect payment provider calls, retries, and timeout behavior.",
                "Verify queue depth and isolate the first failing transaction path.",
            ])
        elif root_cause == "Cache Failure":
            recommendations.extend([
                "Confirm cache cluster health, eviction pressure, and connectivity.",
                "Review fallback behavior to prevent load amplification on upstream systems.",
            ])
        elif root_cause == "Gateway Failure":
            recommendations.extend([
                "Check routing, load balancer, and ingress configuration.",
                "Validate health checks and upstream dependency reachability.",
            ])
        else:
            recommendations.append("Inspect the earliest error and correlate it with recent deployment or infrastructure changes.")

        if severity == "Critical":
            recommendations.append("Escalate immediately and assign an incident commander.")
        elif severity == "Medium":
            recommendations.append("Increase monitoring and validate service recovery after mitigation.")
        else:
            recommendations.append("Track recurrence and review the service for latent instability.")

        if services:
            recommendations.append(f"Focus triage on the dependency chain involving {services[0]}.")

        return recommendations

    def _build_explanation(
        self,
        root_cause: str,
        evidence: list[dict[str, Any]],
        prediction: str,
        recommendations: list[str],
    ) -> str:
        evidence_summary = evidence[0]["message"] if evidence else "No direct evidence matched the current heuristics."
        return (
            f"Root cause assessment: {root_cause}. "
            f"Supporting evidence: {evidence_summary}. "
            f"Cascade assessment: {prediction} "
            f"Primary recommendations: {recommendations[0]}"
        )