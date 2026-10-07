"""Provider boundary for the review-only Gemini AI Agent."""

from __future__ import annotations

from typing import Protocol

from flow_otomatis.domain.gemini import GeminiAgentContext, GeminiAgentReply


class GeminiAgentProviderError(RuntimeError):
    """A sanitized Gemini provider failure safe to surface to the application."""


class GeminiAgentProviderPort(Protocol):
    """Generate one advisory response without executing any application action."""

    def generate(
        self,
        api_key: str,
        context: GeminiAgentContext,
        user_message: str,
    ) -> GeminiAgentReply:
        """Return text and a review-only proposal."""
        ...
