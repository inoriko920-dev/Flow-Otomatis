from __future__ import annotations

import threading
import time
from datetime import UTC, datetime

import pytest

from flow_otomatis.application.ports.google_session import (
    GoogleSessionProfile,
    GoogleSessionRestartGate,
    GoogleSessionState,
)
from flow_otomatis.domain.errors import FlowOtomatisError
from flow_otomatis.workers.browser.google_session_commands import (
    ThreadedGoogleSessionCommands,
)


class ThreadAwareSessionPort:
    """Fixture session port that exposes only safe metadata and thread evidence."""

    def __init__(self, *, slow_check: bool = False) -> None:
        self.profile = GoogleSessionProfile(
            profile_id="profile-0123456789ab",
            label="Akun Worker",
            state=GoogleSessionState.NEEDS_LOGIN,
            last_checked_at=None,
            detail="Login manual diperlukan.",
        )
        self.slow_check = slow_check
        self.started = threading.Event()
        self.release = threading.Event()
        self.shutdown_called = threading.Event()
        self.thread_ids: list[int] = []

    def _record_thread(self) -> None:
        self.thread_ids.append(threading.get_ident())

    def list_profiles(self) -> tuple[GoogleSessionProfile, ...]:
        return (self.profile,)

    def create_profile(self, label: str) -> GoogleSessionProfile:
        del label
        return self.profile

    def open_login(self, profile_id: str) -> GoogleSessionProfile:
        assert profile_id == self.profile.profile_id
        self._record_thread()
        return self.profile

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        assert profile_id == self.profile.profile_id
        self._record_thread()
        self.started.set()
        if self.slow_check:
            assert self.release.wait(timeout=2.0)
        self.profile = GoogleSessionProfile(
            profile_id=self.profile.profile_id,
            label=self.profile.label,
            state=GoogleSessionState.READY,
            last_checked_at=datetime.now(UTC),
            detail="Sesi Google terotorisasi dan siap digunakan.",
        )
        return self.profile

    def get_restart_gate(self, profile_id: str) -> GoogleSessionRestartGate:
        return GoogleSessionRestartGate(
            profile_id=profile_id,
            current_state=self.profile.state,
            first_ready_at=self.profile.last_checked_at,
            restart_verified_at=None,
        )

    def cancel_profile(self, profile_id: str) -> None:
        assert profile_id == self.profile.profile_id
        self._record_thread()

    def delete_profile(self, profile_id: str) -> None:
        assert profile_id == self.profile.profile_id
        self._record_thread()

    def shutdown(self) -> None:
        self._record_thread()
        self.shutdown_called.set()


def test_browser_commands_use_one_owner_and_reject_same_profile_duplicate() -> None:
    port = ThreadAwareSessionPort(slow_check=True)
    commands = ThreadedGoogleSessionCommands(port)

    first = commands.submit_check_profile(port.profile.profile_id)
    assert port.started.wait(timeout=1.0)

    duplicate = commands.submit_check_profile(port.profile.profile_id)
    with pytest.raises(FlowOtomatisError, match="masih berjalan"):
        duplicate.result(timeout=0.2)

    port.release.set()
    checked = first.result(timeout=1.0)
    opened = commands.submit_open_login(port.profile.profile_id).result(timeout=1.0)

    assert checked.state is GoogleSessionState.READY
    assert opened.profile_id == port.profile.profile_id
    assert len(set(port.thread_ids)) == 1
    assert port.thread_ids[0] != threading.get_ident()
    assert not hasattr(checked, "page")
    assert not hasattr(checked, "browser")
    assert commands.shutdown(timeout_s=1.0) is True
    assert port.shutdown_called.is_set()
    assert len(set(port.thread_ids)) == 1


def test_browser_command_shutdown_wait_is_bounded_during_slow_probe() -> None:
    port = ThreadAwareSessionPort(slow_check=True)
    commands = ThreadedGoogleSessionCommands(port)
    active = commands.submit_check_profile(port.profile.profile_id)
    assert port.started.wait(timeout=1.0)

    started = time.monotonic()
    completed = commands.shutdown(timeout_s=0.02)
    elapsed = time.monotonic() - started

    assert completed is False
    assert elapsed < 0.25

    port.release.set()
    assert active.result(timeout=1.0).state is GoogleSessionState.READY
    assert port.shutdown_called.wait(timeout=1.0)


def test_check_all_is_serial_and_returns_only_sanitized_profiles() -> None:
    port = ThreadAwareSessionPort()
    commands = ThreadedGoogleSessionCommands(port)

    result = commands.submit_check_all((port.profile.profile_id,)).result(timeout=1.0)

    assert result == (port.profile,)
    serialized = repr(result).casefold()
    for forbidden in ("cookie", "password", "credential", "browsercontext", "playwright"):
        assert forbidden not in serialized
    assert commands.shutdown(timeout_s=1.0) is True
