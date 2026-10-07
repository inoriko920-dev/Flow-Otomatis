"""Application-owned ports for Gemini API-key storage and health checking."""

from __future__ import annotations

from typing import Protocol

from flow_otomatis.domain.gemini_key import (
    GeminiKeyHealthResult,
    GeminiKeyHealthState,
    GeminiKeySummary,
)


class GeminiKeyVaultPort(Protocol):
    """Store secret material separately from credential-free metadata."""

    def list_summaries(self) -> tuple[GeminiKeySummary, ...]:
        """List safe metadata without returning any full key."""

    def save_key(
        self,
        *,
        key_id: str,
        label: str,
        api_key: str,
        masked_key: str,
        fingerprint: str,
    ) -> GeminiKeySummary:
        """Persist one secret and its safe metadata."""

    def get_secret(self, key_id: str) -> str:
        """Read one full key for provider use only."""

    def set_active(self, key_id: str) -> GeminiKeySummary:
        """Explicitly select one key; never rotate automatically."""

    def update_health(
        self,
        key_id: str,
        state: GeminiKeyHealthState,
        detail: str,
    ) -> GeminiKeySummary:
        """Persist a sanitized health outcome."""

    def delete_key(self, key_id: str) -> None:
        """Delete one secret and its safe metadata."""


class GeminiKeyHealthProbePort(Protocol):
    """Perform one read-only/non-generating key health request."""

    def check(self, api_key: str) -> GeminiKeyHealthResult:
        """Return only sanitized health state/detail."""
