"""Production-only Settings uses local facts, not frozen sample provider UI."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from PySide6.QtWidgets import QLabel, QPushButton

from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.presentation.main_window import MainWindow


def _label_texts(window: MainWindow) -> str:
    return " ".join(label.text() for label in window.findChildren(QLabel))


def _empty_workspace(*, model: str = "Approved Local Model") -> WorkspaceState:
    now = datetime.now(UTC)
    return WorkspaceState(
        schema_version="1.0",
        episode_id="EP_REAL_SETTINGS",
        project_name="Test Project",
        source_package_path="unused",
        created_at=now,
        imported_at=now,
        model=model,
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(),
    )


def test_production_settings_has_no_fake_provider_or_cloud_autosave_claims(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Pengaturan")
    assert window.fixture_code == "REAL_SETTINGS"
    text = _label_texts(window)
    assert "PENGATURAN TERKUNCI" in text
    assert "belum ada project aktif" in text
    assert "target workflow" in text
    assert "Generate live belum diaktifkan" in text
    assert "bukan cloud sync" in text
    assert "Belum ada Workspace terbuka" in text
    assert "●  Mode Lokal" in text
    assert window._right_host.isHidden()
    window.close()


def test_production_settings_refreshes_from_current_workspace_without_provider(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._current_workspace = _empty_workspace()
    window._open_navigation_item("Pengaturan")
    assert window.fixture_code == "REAL_SETTINGS"
    assert "Approved Local Model • dari Workspace lokal" in _label_texts(window)
    assert "0 Scene" in _label_texts(window)

    window._current_workspace = replace(window._current_workspace, model="Updated Local Model")
    refresh = window.findChild(QPushButton, "RealSettingsRefresh")
    assert refresh is not None and refresh.isEnabled()
    refresh.click()
    text = _label_texts(window)
    assert "Updated Local Model • dari Workspace lokal" in text
    assert "Approved Local Model" not in text
    assert "Generate live belum diaktifkan" in text
    window.close()


def test_frozen_settings_reference_remains_identical_in_fixture_mode(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._open_navigation_item("Pengaturan")
    assert window.fixture_code == "UI-IMG-007A"
    assert window.findChild(QPushButton, "RealSettingsRefresh") is None
    assert "Autosave aktif" in _label_texts(window)
    window.close()
