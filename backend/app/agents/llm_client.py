"""Provider-agnostic AI client boundary for IncidentIQ."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class LlmClient(Protocol):
    """Contract for interchangeable language model providers."""

    def analyze_incident(self, prompt: str) -> str:
        """Return a model-generated analysis for the supplied prompt."""


@dataclass(slots=True)
class OpenAIClient:
    """OpenAI-compatible implementation kept behind a narrow interface."""

    api_key: str
    model: str

    def analyze_incident(self, prompt: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency boundary
            raise RuntimeError("openai package is not installed") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text
