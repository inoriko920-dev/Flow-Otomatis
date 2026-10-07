from __future__ import annotations

from datetime import UTC, datetime

from flow_otomatis.application.ports.google_session import (
    GoogleSessionProfile,
    GoogleSessionRestartGate,
    GoogleSessionState,
)
from flow_otomatis.application.services.google_sessions import GoogleSessionService


class FixtureSessionPort:
    def __init__(self) -> None:
        self.gate = GoogleSessionRestartGate(
            profile_id="profile-0123456789ab",
            current_state=GoogleSessionState.READY,
            first_ready_at=datetime(2026, 10, 7, 10, 0, tzinfo=UTC),
            restart_verified_at=datetime(2026, 10, 7, 10, 5, tzinfo=UTC),
        )

    def list_profiles(self) -> tuple[GoogleSessionProfile, ...]:
        return ()

    def create_profile(self, label: str) -> GoogleSessionProfile:
        raise AssertionError

    def open_login(self, profile_id: str) -> GoogleSessionProfile:
        raise AssertionError

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        raise AssertionError

    def get_restart_gate(self, profile_id: str) -> GoogleSessionRestartGate:
        assert profile_id == self.gate.profile_id
        return self.gate

    def cancel_profile(self, profile_id: str) -> None:
        raise AssertionError

    def delete_profile(self, profile_id: str) -> None:
        raise AssertionError

    def shutdown(self) -> None:
        pass


def test_service_exposes_restart_gate_without_session_secrets() -> None:
    service = GoogleSessionService(FixtureSessionPort())

    gate = service.get_restart_gate("profile-0123456789ab")

    assert gate.ready_after_restart is True
    assert gate.current_state is GoogleSessionState.READY
