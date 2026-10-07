"""Application service for authorized Google session lifecycle."""

from __future__ import annotations

from concurrent.futures import Future

from flow_otomatis.application.ports.google_session import (
    GoogleSessionCommandPort,
    GoogleSessionPort,
    GoogleSessionProfile,
    GoogleSessionRestartGate,
)
from flow_otomatis.domain.errors import FlowOtomatisError


def _completed_future[T](value: T) -> Future[T]:
    future: Future[T] = Future()
    future.set_result(value)
    return future


class GoogleSessionService:
    """Coordinate safe session metadata and dedicated Browser Worker commands."""

    def __init__(
        self,
        sessions: GoogleSessionPort,
        *,
        commands: GoogleSessionCommandPort | None = None,
    ) -> None:
        self._sessions = sessions
        self._commands = commands

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
        """Open login through Browser Worker when the production command port exists."""

        if self._commands is None:
            return self._sessions.open_login(profile_id)
        return self._commands.submit_open_login(profile_id).result()

    def open_login_async(self, profile_id: str) -> Future[GoogleSessionProfile]:
        """Schedule manual-login Chrome work without blocking the Qt event loop."""

        if self._commands is None:
            try:
                return _completed_future(self._sessions.open_login(profile_id))
            except Exception as exc:
                future: Future[GoogleSessionProfile] = Future()
                future.set_exception(exc)
                return future
        return self._commands.submit_open_login(profile_id)

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        """Refresh one profile through Browser Worker when configured."""

        if self._commands is None:
            return self._sessions.check_profile(profile_id)
        return self._commands.submit_check_profile(profile_id).result()

    def check_profile_async(self, profile_id: str) -> Future[GoogleSessionProfile]:
        """Schedule one session probe without blocking the Qt event loop."""

        if self._commands is None:
            try:
                return _completed_future(self._sessions.check_profile(profile_id))
            except Exception as exc:
                future: Future[GoogleSessionProfile] = Future()
                future.set_exception(exc)
                return future
        return self._commands.submit_check_profile(profile_id)

    def check_all(self) -> tuple[GoogleSessionProfile, ...]:
        """Refresh every local profile serially."""

        profile_ids = tuple(profile.profile_id for profile in self.list_profiles())
        if self._commands is None:
            return tuple(self._sessions.check_profile(profile_id) for profile_id in profile_ids)
        return self._commands.submit_check_all(profile_ids).result()

    def check_all_async(self) -> Future[tuple[GoogleSessionProfile, ...]]:
        """Schedule serial checks on the one Browser Worker owner."""

        profile_ids = tuple(profile.profile_id for profile in self.list_profiles())
        if self._commands is None:
            try:
                return _completed_future(
                    tuple(self._sessions.check_profile(profile_id) for profile_id in profile_ids)
                )
            except Exception as exc:
                future: Future[tuple[GoogleSessionProfile, ...]] = Future()
                future.set_exception(exc)
                return future
        return self._commands.submit_check_all(profile_ids)

    def get_restart_gate(self, profile_id: str) -> GoogleSessionRestartGate:
        """Return sanitized evidence that READY survived an application restart."""

        return self._sessions.get_restart_gate(profile_id)

    def cancel_profile(self, profile_id: str) -> None:
        """Close one profile context on Browser Worker when configured."""

        if self._commands is None:
            self._sessions.cancel_profile(profile_id)
            return
        self._commands.submit_cancel_profile(profile_id).result()

    def delete_profile(self, profile_id: str) -> None:
        """Delete one app-local profile after worker-owned browser close."""

        if self._commands is None:
            self._sessions.delete_profile(profile_id)
            return
        self._commands.submit_delete_profile(profile_id).result()

    def shutdown(self, *, timeout_s: float = 2.0) -> bool:
        """Request browser shutdown while bounding how long the caller waits."""

        if self._commands is None:
            self._sessions.shutdown()
            return True
        return self._commands.shutdown(timeout_s=max(timeout_s, 0.0))
