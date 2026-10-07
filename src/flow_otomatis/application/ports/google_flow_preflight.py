"""Application-owned contract for read-only Google Flow access preflight."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol


class GoogleFlowAccessState(StrEnum):
    """Read-only reachability/auth state; this does not mean generation is proven."""

    REACHABLE = "REACHABLE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class GoogleFlowAccessProbe:
    """Sanitized read-only Flow preflight result."""

    profile_id: str
    state: GoogleFlowAccessState
    checked_at: datetime
    detail: str


class GoogleFlowPreflightPort(Protocol):
    """Check Flow reachability without upload, prompt entry, or generation."""

    def check(self, profile_id: str) -> GoogleFlowAccessProbe:
        """Open Flow read-only and return a sanitized state."""

    def close(self, profile_id: str) -> None:
        """Close the profile browser context without deleting session data."""

    def shutdown(self) -> None:
        """Release browser resources owned by this adapter."""
