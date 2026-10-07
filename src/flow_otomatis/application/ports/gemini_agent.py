"""Provider-neutral read-only Gemini Agent boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class GeminiAgentProviderError(RuntimeError):
    """A sanitized provider failure that must not expose the API key or response body."""


@dataclass(frozen=True, slots=True)
class GeminiAgentProviderResult:
    """One text-only provider response."""

    text: str
    model: str


class GeminiAgentProviderPort(Protocol):
    """Generate one text answer without exposing tools or application actions."""

    def ask(
        self,
        *,
        api_key: str,
        system_instruction: str,
        prompt: str,
    ) -> GeminiAgentProviderResult:
        """Return one provider answer using an explicitly supplied secret."""
        ...
