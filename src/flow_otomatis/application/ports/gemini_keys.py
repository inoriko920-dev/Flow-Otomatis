"""Application-owned ports for Gemini key metadata, secrets, and health."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from flow_otomatis.domain.gemini import GeminiKeyProfile, GeminiKeyStatus


@dataclass(frozen=True, slots=True)
class GeminiKeyHealthEvidence:
    """Sanitized Gemini API health result; never contains the raw key."""

    status: GeminiKeyStatus
    detail: str


class GeminiKeyRepositoryPort(Protocol):
    """Persist credential-free Gemini key metadata."""

    def list_profiles(self) -> tuple[GeminiKeyProfile, ...]:
        ...

    def get(self, key_id: str) -> GeminiKeyProfile | None:
        ...

    def find_by_fingerprint(self, fingerprint: str) -> GeminiKeyProfile | None:
        ...

    def save(self, profile: GeminiKeyProfile) -> None:
        ...

    def set_active(self, key_id: str) -> GeminiKeyProfile:
        ...

    def delete(self, key_id: str) -> None:
        ...


class SecretStorePort(Protocol):
    """Store opaque secrets outside project/database exports."""

    def set_secret(self, key_id: str, secret: str) -> None:
        ...

    def get_secret(self, key_id: str) -> str | None:
        ...

    def delete_secret(self, key_id: str) -> None:
        ...


class GeminiKeyHealthPort(Protocol):
    """Check one key against the official Gemini API without exposing it."""

    def check(self, api_key: str) -> GeminiKeyHealthEvidence:
        ...
