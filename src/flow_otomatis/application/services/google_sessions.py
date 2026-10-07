"""Application service for authorized Google session lifecycle."""

from __future__ import annotations

from flow_otomatis.application.ports.google_session import (
    GoogleSessionPort,
    GoogleSessionProfile,
)
from flow_otomatis.domain.errors import FlowOtomatisError


class GoogleSessionService:
    """Coordinate safe profile/session operations without provider details."""

    def __init__(self, sessions: GoogleSessionPort) -> None:
        self._sessions = sessions

    def list_profiles(self) -> tuple[GoogleSessionProfile, ...]:
        """Return profiles in stable human-readable order."""

        return tuple(
            sorted(self._sessions.list_profiles(), key=lambda profile: profile.label.casefold())
        )

    def create_profile(self, label: str) -> GoogleSessionProfile:
        """Create a named profile after validating only non-secret metadata."""

        normalized = " ".join(label.split())
        if not normalized:
            raise FlowOtomatisError("Nama profil Google tidak boleh kosong.")
        if len(normalized) > 80:
            raise FlowOtomatisError("Nama profil Google maksimal 80 karakter.")
        return self._sessions.create_profile(normalized)

    def open_login(self, profile_id: str) -> GoogleSessionProfile:
        """Open/focus the official login page for manual user authentication."""

        return self._sessions.open_login(profile_id)

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        """Refresh one profile authorization state."""

        return self._sessions.check_profile(profile_id)

    def check_all(self) -> tuple[GoogleSessionProfile, ...]:
        """Refresh every local profile serially and return the latest state."""

        return tuple(
            self._sessions.check_profile(profile.profile_id) for profile in self.list_profiles()
        )

    def cancel_profile(self, profile_id: str) -> None:
        """Close one profile browser context without deleting its persisted session."""

        self._sessions.cancel_profile(profile_id)

    def delete_profile(self, profile_id: str) -> None:
        """Delete only the app-local browser profile/session."""

        self._sessions.delete_profile(profile_id)

    def shutdown(self) -> None:
        """Release browser worker resources during application shutdown."""

        self._sessions.shutdown()
