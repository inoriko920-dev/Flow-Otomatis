"""Real production must not use mock account/key profiles without services."""

from __future__ import annotations

from datetime import UTC, datetime

from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from flow_otomatis.application.ports.google_flow_preflight import (
    GoogleFlowAccessProbe,
    GoogleFlowAccessState,
)
from flow_otomatis.presentation.main_window import MainWindow


def _visible_text(window: MainWindow) -> str:
    current = window._content_layout.itemAt(0).widget()
    assert current is not None
    return " ".join(label.text() for label in current.findChildren(QLabel))


def test_unconfigured_google_profile_never_shows_fake_login_or_accounts(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Profil Google")
    assert window.fixture_code == "REAL_GOOGLE_PROFILES_UNAVAILABLE"
    assert window._nav_buttons["Profil Google"].isChecked()
    assert "Pengelola sesi Google" in _visible_text(window)
    assert "LAYANAN TIDAK TERSEDIA" in _visible_text(window)
    assert "saldo" in _visible_text(window)
    assert "Sesi berhasil diverifikasi" not in _visible_text(window)
    assert window._status_project.text() == "Tidak ada bukti akses provider"
    assert window._right_host.isHidden()

    page = window._content_layout.itemAt(0).widget()
    assert isinstance(page, QWidget)
    diagnostic = page.findChild(QPushButton, "RealUnavailableServiceDiagnostics")
    assert diagnostic is not None and diagnostic.isEnabled()
    diagnostic.click()
    assert window.fixture_code == "REAL_DIAGNOSTICS"
    assert window._nav_buttons["Diagnostik"].isChecked()
    window.close()


def test_unconfigured_gemini_keys_has_real_safe_navigation_back_to_hub(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Gemini Keys")
    assert window.fixture_code == "REAL_GEMINI_KEYS_UNAVAILABLE"
    assert window._nav_buttons["Gemini Keys"].isChecked()
    assert "Pengelola kunci Gemini" in _visible_text(window)
    assert "Layanan tidak tersedia".casefold() in _visible_text(window).casefold()
    assert "API key aktif" not in _visible_text(window)
    page = window._content_layout.itemAt(0).widget()
    assert page is not None
    home = page.findChild(QPushButton, "RealUnavailableServiceHome")
    assert home is not None and home.isEnabled()
    home.click()
    assert window.fixture_code == "REAL_PROJECT_HUB_UNAVAILABLE"
    assert window._nav_buttons["Beranda"].isChecked()
    window.close()


def test_unconfigured_provider_routes_are_independent_and_not_mutating(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.configure_production_shell()
    for route, expected in (
        ("Profil Google", "REAL_GOOGLE_PROFILES_UNAVAILABLE"),
        ("Gemini Keys", "REAL_GEMINI_KEYS_UNAVAILABLE"),
        ("Profil Google", "REAL_GOOGLE_PROFILES_UNAVAILABLE"),
    ):
        window._open_navigation_item(route)
        assert window.fixture_code == expected
        assert window._connection_badge.text() == "●  Mode Lokal"
        assert window._status_project.text() == "Tidak ada bukti akses provider"
        assert window._active_uix_preview is None
    window.close()


def test_explicit_frozen_auth_fixture_routes_remain_unchanged(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._open_navigation_item("Profil Google")
    assert window.fixture_code == "UI-IMG-004A"
    window._open_navigation_item("Gemini Keys")
    assert window.fixture_code == "UI-IMG-006A"
    page = window._content_layout.itemAt(0).widget()
    assert page is not None
    assert page.objectName() != "RealGeminiKeysUnavailable"
    window.close()


def test_direct_profile_and_key_refresh_cannot_open_mock_accounts_in_production(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.configure_production_shell()

    window.show_google_profiles()
    assert window.fixture_code == "REAL_GOOGLE_PROFILES_UNAVAILABLE"
    assert "LAYANAN TIDAK TERSEDIA" in _visible_text(window)

    window.show_gemini_keys()
    assert window.fixture_code == "REAL_GEMINI_KEYS_UNAVAILABLE"
    assert "LAYANAN TIDAK TERSEDIA" in _visible_text(window)
    assert window._active_google_profile_id is None
    window.close()


def test_unreadable_google_profile_metadata_fails_closed_without_leaking_paths(qtbot) -> None:
    class CorruptSessions:
        def list_profiles(self):
            raise OSError("C:/private/google/profile/cookie.sqlite")

    window = MainWindow(google_session_service=CorruptSessions())
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Profil Google")
    assert window.fixture_code == "REAL_GOOGLE_PROFILES_UNAVAILABLE"
    text = _visible_text(window)
    assert "STATUS LAYANAN TIDAK DIKETAHUI" in text
    assert "Data tersimpan tidak diubah" in text
    assert "cookie.sqlite" not in text
    assert "C:/private" not in text
    assert window._project_label.text() == "Data lokal belum dapat dibaca"
    assert window._connection_badge.text() == "●  Mode Lokal"
    window.close()


def test_unreadable_gemini_key_metadata_cannot_be_mistaken_for_zero_keys(qtbot) -> None:
    class CorruptKeys:
        def list_profiles(self):
            raise OSError("C:/private/api-keys.txt")

    window = MainWindow(gemini_key_service=CorruptKeys())
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Gemini Keys")
    assert window.fixture_code == "REAL_GEMINI_KEYS_UNAVAILABLE"
    text = _visible_text(window)
    assert "STATUS LAYANAN TIDAK DIKETAHUI" in text
    assert "api-keys.txt" not in text
    assert "0 key" not in text
    assert window._status_project.text() == "Tidak ada bukti akses provider"
    window.close()


def test_stale_flow_probe_after_profile_storage_failure_is_revoked(qtbot) -> None:
    class UnreadableSessions:
        def list_profiles(self):
            raise OSError("C:/private/browser-profile/cookies.sqlite")

    window = MainWindow(google_session_service=UnreadableSessions())
    qtbot.addWidget(window)
    window.configure_production_shell()
    profile_id = "profile-safe-test"
    window._fixture_code = "REAL_GOOGLE_LOGIN"
    window._active_google_profile_id = profile_id
    window._google_flow_epochs[profile_id] = 3
    window._google_flow_busy.add(profile_id)

    probe = GoogleFlowAccessProbe(
        profile_id=profile_id,
        state=GoogleFlowAccessState.REACHABLE_ONLY,
        checked_at=datetime.now(UTC),
        detail="Untrusted result from a pending worker",
    )
    window._on_google_flow_checked(profile_id, 3, probe)

    assert window.fixture_code == "REAL_GOOGLE_PROFILES_UNAVAILABLE"
    assert window._active_google_profile_id is None
    assert profile_id not in window._google_flow_busy
    assert profile_id not in window._google_flow_probes
    assert window._google_flow_epochs[profile_id] > 3
    assert "cookies.sqlite" not in _visible_text(window)

    # An exact late duplicate is fenced by the incremented epoch.
    window._on_google_flow_checked(profile_id, 3, probe)
    assert profile_id not in window._google_flow_probes
    assert window.fixture_code == "REAL_GOOGLE_PROFILES_UNAVAILABLE"
    window.close()
