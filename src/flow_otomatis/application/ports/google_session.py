"""Application-owned contract for authorized Google browser sessions."""

from __future__ import annotations

from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from flow_otomatis.application.ports.google_flow_preflight import GoogleFlowAccessProbe


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


@dataclass(frozen=True, slots=True)
class GoogleSessionRestartGate:
    """Credential-free proof that READY was observed again after an app restart."""

    profile_id: str
    current_state: GoogleSessionState
    first_ready_at: datetime | None
    restart_verified_at: datetime | None

    @property
    def ready_after_restart(self) -> bool:
        return (
            self.current_state is GoogleSessionState.READY and self.restart_verified_at is not None
        )


class GoogleSessionPort(Protocol):
    """Synchronous session adapter owned below the Browser Worker boundary."""

    def list_profiles(self) -> tuple[GoogleSessionProfile, ...]:
        """Return safe local profile metadata."""

    def create_profile(self, label: str) -> GoogleSessionProfile:
        """Create one isolated persistent user-owned browser profile."""

    def open_login(self, profile_id: str) -> GoogleSessionProfile:
        """Open/focus the official manual Google login surface."""

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        """Probe whether the profile is authorized without reading credentials."""

    def get_restart_gate(self, profile_id: str) -> GoogleSessionRestartGate:
        """Return sanitized restart-persistence evidence for one profile."""

    def cancel_profile(self, profile_id: str) -> None:
        """Close the active browser context for one profile."""

    def delete_profile(self, profile_id: str) -> None:
        """Delete only the app-local profile/session directory."""

    def shutdown(self) -> None:
        """Close all browser resources owned by the adapter."""


class GoogleSessionCommandPort(Protocol):
    """Asynchronous command boundary for browser-touching session operations."""

    def submit_open_login(self, profile_id: str) -> Future[GoogleSessionProfile]:
        """Schedule manual-login Chrome creation on the Browser Worker owner."""

    def submit_check_profile(self, profile_id: str) -> Future[GoogleSessionProfile]:
        """Schedule one authorization probe on the Browser Worker owner."""

    def submit_check_all(
        self,
        profile_ids: tuple[str, ...],
    ) -> Future[tuple[GoogleSessionProfile, ...]]:
        """Schedule serial authorization probes on the Browser Worker owner."""

    def submit_check_flow(self, profile_id: str) -> Future[GoogleFlowAccessProbe]:
        """Queue read-only Flow preflight on the session owner's single thread."""

    def submit_cancel_profile(self, profile_id: str) -> Future[None]:
        """Schedule profile browser shutdown without transferring runtime ownership."""

    def submit_delete_profile(self, profile_id: str) -> Future[None]:
        """Schedule profile close/delete on the Browser Worker owner."""

    def shutdown(self, *, timeout_s: float) -> bool:
        """Request worker-owned shutdown and wait no longer than the bounded policy."""
