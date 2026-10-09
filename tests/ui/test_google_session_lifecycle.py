from __future__ import annotations

import threading
from datetime import UTC, datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QPushButton

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
