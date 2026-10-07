"""Gemini API-key metadata. Raw secrets never belong in domain state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class GeminiKeyStatus(StrEnum):
    """Safe health status for one stored Gemini key."""

    UNCHECKED = "UNCHECKED"
    VALID = "VALID"
    INVALID = "INVALID"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class GeminiKeyProfile:
    """Credential-free metadata displayed by the application."""

    key_id: str
    label: str
    masked_key: str
    fingerprint: str
    status: GeminiKeyStatus
    last_checked_at: datetime | None
    is_active: bool
    detail: str
