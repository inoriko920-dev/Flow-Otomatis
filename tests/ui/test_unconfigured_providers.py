"""Real production must not use mock account/key profiles without services."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QWidget

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
