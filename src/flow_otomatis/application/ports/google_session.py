"""Application-owned contract for authorized Google browser sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol


class GoogleSessionState(StrEnum):
    """Credential-free lifecycle state exposed to the application."""

    READY = "READY"
    NEEDS_LOGIN = "NEEDS_LOGIN"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class GoogleSessionProfile:
    """Safe profile metadata; browser cookies/tokens never cross this contract."""

    profile_id: str
    label: str
    state: GoogleSessionState
    last_checked_at: datetime | None
    detail: str


class GoogleSessionPort(Protocol):
    """Port implemented only by the browser/session boundary."""

    def list_profiles(self) -> tuple[GoogleSessionProfile, ...]:
        """Return safe local profile metadata."""

    def create_profile(self, label: str) -> GoogleSessionProfile:
        """Create one isolated persistent user-owned browser profile."""

    def open_login(self, profile_id: str) -> GoogleSessionProfile:
        """Open/focus the official manual Google login surface."""

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        """Probe whether the profile is authorized without reading credentials."""

    def cancel_profile(self, profile_id: str) -> None:
        """Close the active browser context for one profile."""

    def delete_profile(self, profile_id: str) -> None:
        """Delete only the app-local profile/session directory."""

    def shutdown(self) -> None:
        """Close all browser resources owned by the adapter."""
