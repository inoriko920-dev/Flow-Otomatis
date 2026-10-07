"""Credential-free Gemini key metadata and import/health state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class GeminiKeyHealthState(StrEnum):
    """Safe health state persisted without storing provider response bodies."""

    UNCHECKED = "UNCHECKED"
    HEALTHY = "HEALTHY"
    RATE_LIMITED = "RATE_LIMITED"
    INVALID = "INVALID"
    ERROR = "ERROR"


class GeminiKeyImportStatus(StrEnum):
    """Structural import preview outcome; this is not a remote health check."""

    NEW = "NEW"
    DUPLICATE = "DUPLICATE"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class GeminiKeySummary:
    """Credential-free metadata safe for UI and diagnostics."""

    key_id: str
    label: str
    masked_key: str
    fingerprint: str
    active: bool
    health_state: GeminiKeyHealthState
    last_checked_at: datetime | None
    detail: str


@dataclass(frozen=True, slots=True)
class GeminiKeyHealthResult:
    """Sanitized result from one non-generating Gemini health probe."""

    state: GeminiKeyHealthState
    detail: str


@dataclass(frozen=True, slots=True)
class GeminiKeyImportItem:
    """One masked line in an import preview."""

    row_number: int
    label: str
    masked_key: str
    status: GeminiKeyImportStatus


@dataclass(frozen=True, slots=True)
class GeminiKeyImportPreview:
    """Opaque import transaction; raw keys never enter this DTO."""

    preview_id: str
    items: tuple[GeminiKeyImportItem, ...]

    @property
    def new_count(self) -> int:
        return sum(item.status is GeminiKeyImportStatus.NEW for item in self.items)

    @property
    def duplicate_count(self) -> int:
        return sum(item.status is GeminiKeyImportStatus.DUPLICATE for item in self.items)

    @property
    def invalid_count(self) -> int:
        return sum(item.status is GeminiKeyImportStatus.INVALID for item in self.items)
