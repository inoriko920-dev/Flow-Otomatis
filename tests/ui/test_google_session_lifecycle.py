from __future__ import annotations

from datetime import UTC, datetime

from PySide6.QtWidgets import QLabel, QPushButton

from flow_otomatis.application.ports.google_session import (
    GoogleSessionProfile,
    GoogleSessionState,
)
from flow_otomatis.application.services import GoogleSessionService
from flow_otomatis.presentation.main_window import MainWindow


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
