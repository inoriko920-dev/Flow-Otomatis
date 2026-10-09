from __future__ import annotations

import threading
from concurrent.futures import Future
from datetime import UTC, datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton

from flow_otomatis.application.ports.google_flow_preflight import (
    GoogleFlowAccessProbe,
    GoogleFlowAccessState,
)
from flow_otomatis.application.ports.google_session import (
    GoogleSessionProfile,
    GoogleSessionRestartGate,
    GoogleSessionState,
)
from flow_otomatis.application.services import GoogleFlowPreflightService, GoogleSessionService
from flow_otomatis.presentation.main_window import MainWindow
from flow_otomatis.workers.browser.google_session_commands import (
    ThreadedGoogleSessionCommands,
)


class FixtureSessionPort:
    def __init__(self) -> None:
        self.profile = GoogleSessionProfile(
            profile_id="profile-0123456789ab",
            label="Akun Produksi Saya",
            state=GoogleSessionState.NEEDS_LOGIN,
            last_checked_at=None,
            detail="Login manual diperlukan.",
        )
        self.opened = False
        self.restart_verified = False

    def list_profiles(self) -> tuple[GoogleSessionProfile, ...]:
        return (self.profile,)

    def create_profile(self, label: str) -> GoogleSessionProfile:
        self.profile = GoogleSessionProfile(
            profile_id=self.profile.profile_id,
            label=label,
            state=GoogleSessionState.NEEDS_LOGIN,
            last_checked_at=None,
            detail="Login manual diperlukan.",
        )
        return self.profile

    def open_login(self, profile_id: str) -> GoogleSessionProfile:
        assert profile_id == self.profile.profile_id
        self.opened = True
        return self.profile

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        assert profile_id == self.profile.profile_id
        self.profile = GoogleSessionProfile(
            profile_id=self.profile.profile_id,
            label=self.profile.label,
            state=GoogleSessionState.READY,
            last_checked_at=datetime.now(UTC),
            detail="Sesi Google terotorisasi dan siap digunakan.",
        )
        return self.profile

    def get_restart_gate(self, profile_id: str) -> GoogleSessionRestartGate:
        assert profile_id == self.profile.profile_id
        return GoogleSessionRestartGate(
            profile_id=profile_id,
            current_state=self.profile.state,
            first_ready_at=self.profile.last_checked_at,
            restart_verified_at=(datetime.now(UTC) if self.restart_verified else None),
        )

    def cancel_profile(self, profile_id: str) -> None:
        assert profile_id == self.profile.profile_id

    def delete_profile(self, profile_id: str) -> None:
        assert profile_id == self.profile.profile_id

    def shutdown(self) -> None:
        pass


def _button(window: MainWindow, text: str) -> QPushButton:
    return next(button for button in window.findChildren(QPushButton) if button.text() == text)


def test_real_google_profile_navigation_and_manual_login(qtbot) -> None:
    port = FixtureSessionPort()
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)

    window._open_navigation_item("Profil Google")
    assert window.fixture_code == "REAL_GOOGLE_PROFILES"

    _button(window, "Buka / Fokuskan Sesi Login").click()
    assert port.opened is True
    assert window.fixture_code == "REAL_GOOGLE_LOGIN"

    _button(window, "Cek Ulang Sesi").click()
    assert window.fixture_code == "REAL_GOOGLE_LOGIN"
    labels = [label.text() for label in window.findChildren(QLabel)]
    assert "Sesi berhasil diverifikasi" in labels
    assert "Restart belum diverifikasi" in labels
    assert "Belum lulus" in labels


def test_google_login_view_shows_restart_gate_pass(qtbot) -> None:
    port = FixtureSessionPort()
    port.profile = GoogleSessionProfile(
        profile_id=port.profile.profile_id,
        label=port.profile.label,
        state=GoogleSessionState.READY,
        last_checked_at=datetime.now(UTC),
        detail="Sesi Google terotorisasi dan siap digunakan.",
    )
    port.restart_verified = True
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)

    window.show_google_login(port.profile)

    labels = [label.text() for label in window.findChildren(QLabel)]
    assert "Restart berhasil diverifikasi" in labels
    assert "Lulus" in labels


class SlowFixtureSessionPort(FixtureSessionPort):
    def __init__(self) -> None:
        super().__init__()
        self.started = threading.Event()
        self.release = threading.Event()

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        assert profile_id == self.profile.profile_id
        self.started.set()
        assert self.release.wait(timeout=2.0)
        return super().check_profile(profile_id)


def test_slow_session_probe_keeps_qt_heartbeat_responsive(qtbot) -> None:
    port = SlowFixtureSessionPort()
    commands = ThreadedGoogleSessionCommands(port)
    service = GoogleSessionService(port, commands=commands)
    window = MainWindow(google_session_service=service)
    qtbot.addWidget(window)
    window.show_google_login(port.profile)

    heartbeat: list[int] = []
    timer = QTimer(window)
    timer.setInterval(10)
    timer.timeout.connect(lambda: heartbeat.append(len(heartbeat) + 1))
    timer.start()

    _button(window, "Cek Ulang Sesi").click()
    assert port.started.wait(timeout=1.0)

    qtbot.wait(120)
    assert len(heartbeat) >= 3
    assert window.fixture_code == "REAL_GOOGLE_LOGIN"

    port.release.set()
    qtbot.waitUntil(
        lambda: (
            "Sesi berhasil diverifikasi" in [label.text() for label in window.findChildren(QLabel)]
        ),
        timeout=1500,
    )

    assert window.fixture_code == "REAL_GOOGLE_LOGIN"
    assert service.shutdown(timeout_s=1.0) is True


class FixtureFlowPreflight:
    def __init__(self) -> None:
        self.checked: list[str] = []

    def check(self, profile_id: str) -> GoogleFlowAccessProbe:
        self.checked.append(profile_id)
        return GoogleFlowAccessProbe(
            profile_id=profile_id,
            state=GoogleFlowAccessState.REACHABLE_ONLY,
            checked_at=datetime.now(UTC),
            detail="Halaman Flow dapat dijangkau; akses akun belum terverifikasi.",
        )

    def close(self, profile_id: str) -> None:
        del profile_id

    def shutdown(self) -> None:
        pass


def test_real_flow_button_uses_only_read_only_preflight(qtbot) -> None:
    session = FixtureSessionPort()
    session.check_profile(session.profile.profile_id)
    flow = FixtureFlowPreflight()
    window = MainWindow(
        google_session_service=GoogleSessionService(session),
        google_flow_preflight_service=GoogleFlowPreflightService(flow),
    )
    qtbot.addWidget(window)
    window.show_google_login(session.profile)
    _button(window, "Cek Akses Flow").click()
    qtbot.waitUntil(lambda: bool(flow.checked), timeout=1500)

    labels = [label.text() for label in window.findChildren(QLabel)]
    assert session.profile.profile_id in flow.checked
    assert "Halaman terjangkau; akses belum terverifikasi" in labels
    assert "Akses terverifikasi" not in labels


def test_flow_button_requires_current_google_ready(qtbot) -> None:
    session = FixtureSessionPort()
    flow = FixtureFlowPreflight()
    window = MainWindow(
        google_session_service=GoogleSessionService(session),
        google_flow_preflight_service=GoogleFlowPreflightService(flow),
    )
    qtbot.addWidget(window)
    window.show_google_login(session.profile)

    assert not _button(window, "Cek Akses Flow").isEnabled()
    assert flow.checked == []


class DeferredFlowCommands:
    def __init__(self) -> None:
        self.requested: list[tuple[str, Future[GoogleFlowAccessProbe]]] = []

    def submit_check_flow(self, profile_id: str) -> Future[GoogleFlowAccessProbe]:
        future: Future[GoogleFlowAccessProbe] = Future()
        self.requested.append((profile_id, future))
        return future


def test_flow_reply_from_another_profile_never_populates_selected_account(qtbot) -> None:
    session = FixtureSessionPort()
    session.check_profile(session.profile.profile_id)
    commands = DeferredFlowCommands()
    window = MainWindow(
        google_session_service=GoogleSessionService(session),
        google_flow_preflight_service=GoogleFlowPreflightService(
            FixtureFlowPreflight(), commands=commands
        ),
    )
    qtbot.addWidget(window)
    window.show_google_login(session.profile)
    _button(window, "Cek Akses Flow").click()
    assert len(commands.requested) == 1
    assert not _button(window, "Cek Akses Flow").isEnabled()

    commands.requested[0][1].set_result(
        GoogleFlowAccessProbe(
            profile_id="profile-ffffffffffff",
            state=GoogleFlowAccessState.REACHABLE_ONLY,
            checked_at=datetime.now(UTC),
            detail="Fixture only; wrong account.",
        )
    )
    qtbot.waitUntil(lambda: _button(window, "Cek Akses Flow").isEnabled(), timeout=1500)
    labels = [label.text() for label in window.findChildren(QLabel)]
    assert "Halaman terjangkau; akses belum terverifikasi" not in labels
    assert "Belum diperiksa" in labels


def test_flow_reply_after_session_epoch_invalidated_is_ignored(qtbot) -> None:
    session = FixtureSessionPort()
    session.check_profile(session.profile.profile_id)
    commands = DeferredFlowCommands()
    window = MainWindow(
        google_session_service=GoogleSessionService(session),
        google_flow_preflight_service=GoogleFlowPreflightService(
            FixtureFlowPreflight(), commands=commands
        ),
    )
    qtbot.addWidget(window)
    window.show_google_login(session.profile)
    _button(window, "Cek Akses Flow").click()

    window._invalidate_google_flow(session.profile.profile_id)
    commands.requested[0][1].set_result(
        GoogleFlowAccessProbe(
            profile_id=session.profile.profile_id,
            state=GoogleFlowAccessState.REACHABLE_ONLY,
            checked_at=datetime.now(UTC),
            detail="Fixture only; stale callback.",
        )
    )
    qtbot.wait(50)
    assert session.profile.profile_id not in window._google_flow_probes


def test_pending_flow_preflight_does_not_block_qt_heartbeat(qtbot) -> None:
    session = FixtureSessionPort()
    session.check_profile(session.profile.profile_id)
    commands = DeferredFlowCommands()
    window = MainWindow(
        google_session_service=GoogleSessionService(session),
        google_flow_preflight_service=GoogleFlowPreflightService(
            FixtureFlowPreflight(), commands=commands
        ),
    )
    qtbot.addWidget(window)
    window.show_google_login(session.profile)

    heartbeat: list[int] = []
    timer = QTimer(window)
    timer.setInterval(10)
    timer.timeout.connect(lambda: heartbeat.append(len(heartbeat) + 1))
    timer.start()
    _button(window, "Cek Akses Flow").click()
    assert len(commands.requested) == 1

    qtbot.wait(120)
    assert len(heartbeat) >= 3
    assert not _button(window, "Cek Akses Flow").isEnabled()

    commands.requested[0][1].set_result(
        GoogleFlowAccessProbe(
            profile_id=session.profile.profile_id,
            state=GoogleFlowAccessState.REACHABLE_ONLY,
            checked_at=datetime.now(UTC),
            detail="Fixture read-only preflight.",
        )
    )
    qtbot.waitUntil(lambda: _button(window, "Cek Akses Flow").isEnabled(), timeout=1500)


def test_flow_reply_after_window_closed_does_not_change_status(qtbot) -> None:
    session = FixtureSessionPort()
    session.check_profile(session.profile.profile_id)
    commands = DeferredFlowCommands()
    window = MainWindow(
        google_session_service=GoogleSessionService(session),
        google_flow_preflight_service=GoogleFlowPreflightService(
            FixtureFlowPreflight(), commands=commands
        ),
    )
    qtbot.addWidget(window)
    window.show_google_login(session.profile)
    _button(window, "Cek Akses Flow").click()
    assert len(commands.requested) == 1

    window.close()
    commands.requested[0][1].set_result(
        GoogleFlowAccessProbe(
            profile_id=session.profile.profile_id,
            state=GoogleFlowAccessState.REACHABLE_ONLY,
            checked_at=datetime.now(UTC),
            detail="Fixture stale response after close.",
        )
    )
    qtbot.wait(50)
    assert window._google_flow_probes == {}


def test_late_google_check_all_cannot_reopen_profiles_after_navigation(qtbot) -> None:
    port = FixtureSessionPort()
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)
    window.show_google_profiles()

    future: Future[tuple[GoogleSessionProfile, ...]] = Future()
    request = window._begin_google_session_request("check_all", None)
    window._watch_google_all_future(future, request, "Profil Google")
    window.show_fixture("UI-IMG-001A")
    future.set_result((port.profile,))
    assert window.fixture_code == "UI-IMG-001A"
    assert window._active_google_session_request is None
    window.close()


def test_late_google_open_cannot_override_newer_request_on_same_route(qtbot) -> None:
    port = FixtureSessionPort()
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)
    window.show_google_profiles()
    old: Future[GoogleSessionProfile] = Future()
    newer: Future[GoogleSessionProfile] = Future()
    req_old = window._begin_google_session_request("open", port.profile.profile_id)
    window._watch_google_profile_future(old, req_old, "Bantuan Login")
    req_new = window._begin_google_session_request("check", port.profile.profile_id)
    window._watch_google_profile_future(newer, req_new, "Profil Google")

    old.set_result(port.profile)
    assert window.fixture_code == "REAL_GOOGLE_PROFILES"
    assert window._active_google_session_request == req_new
    newer.set_result(port.profile)
    assert window.fixture_code == "REAL_GOOGLE_PROFILES"
    assert window._active_google_session_request is None
    window.close()


def test_late_google_recheck_ignored_after_return_to_account_list(qtbot) -> None:
    port = FixtureSessionPort()
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)
    window.show_google_login(port.profile)
    future: Future[GoogleSessionProfile] = Future()
    request = window._begin_google_session_request("recheck", port.profile.profile_id)
    window._watch_google_profile_future(future, request, "Bantuan Login")

    window.show_google_profiles()
    future.set_result(port.profile)
    assert window.fixture_code == "REAL_GOOGLE_PROFILES"
    assert window._active_google_profile_id is None
    window.close()


def test_late_google_session_error_does_not_warn_unrelated_route(qtbot, monkeypatch) -> None:
    port = FixtureSessionPort()
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)
    window.show_google_profiles()
    errors: list[str] = []
    monkeypatch.setattr(
        QMessageBox, "warning", lambda _window, title, _message: errors.append(title)
    )

    failed: Future[GoogleSessionProfile] = Future()
    request = window._begin_google_session_request("check", port.profile.profile_id)
    window._watch_google_profile_future(failed, request, "Profil Google")
    window.show_fixture("UI-IMG-007A")
    failed.set_exception(RuntimeError("private browser worker detail"))
    assert errors == []
    assert window.fixture_code == "UI-IMG-007A"
    window.close()


def test_google_session_reply_for_other_profile_never_switches_account(qtbot) -> None:
    port = FixtureSessionPort()
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)
    window.show_google_profiles()
    future: Future[GoogleSessionProfile] = Future()
    request = window._begin_google_session_request("open", port.profile.profile_id)
    window._watch_google_profile_future(future, request, "Bantuan Login")
    wrong = GoogleSessionProfile(
        profile_id="profile-ffffffffffff",
        label="Different account",
        state=GoogleSessionState.READY,
        last_checked_at=datetime.now(UTC),
        detail="Untrusted crossed reply",
    )
    future.set_result(wrong)
    assert window.fixture_code == "REAL_GOOGLE_PROFILES"
    assert window._active_google_session_request is None
    window.close()


def test_flow_preflight_fails_closed_on_unreadable_restart_gate(qtbot, monkeypatch) -> None:
    port = FixtureSessionPort()
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)
    window.show_google_login(port.profile)
    monkeypatch.setattr(window, "_google_flow_preflight_service", object())

    def unreadable(_profile_id: str) -> GoogleSessionRestartGate:
        raise OSError("sensitive/private-profile.sqlite")

    monkeypatch.setattr(port, "get_restart_gate", unreadable)
    window._check_active_google_flow()
    assert window.fixture_code == "REAL_GOOGLE_PROFILES_UNAVAILABLE"
    assert window._active_google_profile_id is None
    assert not window._google_flow_busy
    assert not window._google_flow_probes
    window.close()


def test_flow_preflight_fails_closed_if_profile_disappears_after_gate(
    qtbot, monkeypatch
) -> None:
    port = FixtureSessionPort()
    port.check_profile(port.profile.profile_id)
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)
    window.show_google_login(port.profile)
    monkeypatch.setattr(window, "_google_flow_preflight_service", object())
    monkeypatch.setattr(port, "list_profiles", lambda: ())

    window._check_active_google_flow()
    assert window.fixture_code == "REAL_GOOGLE_PROFILES_UNAVAILABLE"
    assert not window._google_flow_busy
    assert not window._google_flow_probes
    window.close()


def test_late_flow_login_refresh_fails_closed_if_profile_metadata_corrupt(
    qtbot, monkeypatch
) -> None:
    port = FixtureSessionPort()
    window = MainWindow(google_session_service=GoogleSessionService(port))
    qtbot.addWidget(window)
    window.show_google_login(port.profile)

    def unreadable() -> tuple[GoogleSessionProfile, ...]:
        raise OSError("private-session-directory")

    monkeypatch.setattr(port, "list_profiles", unreadable)
    window._refresh_active_google_login(port.profile.profile_id)
    assert window.fixture_code == "REAL_GOOGLE_PROFILES_UNAVAILABLE"
    assert window._active_google_profile_id is None
    window.close()
