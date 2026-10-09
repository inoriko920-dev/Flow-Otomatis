"""Project-hub storage failures must be recoverable, not a false empty list."""

from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtWidgets import QLabel, QPushButton

from flow_otomatis.presentation.main_window import MainWindow


class FlakyLibrary:
    def __init__(self) -> None:
        self.fail = True
        self.calls = 0

    def scan_recent(self, limit: int = 10):
        self.calls += 1
        if self.fail:
            raise OSError("PRIVATE_DISK_LOCATION/projects: readonly")
        return SimpleNamespace(workspaces=(), issues=())


def _text(window: MainWindow) -> str:
    return " ".join(label.text() for label in window.findChildren(QLabel))


def test_project_library_read_failure_shows_retry_without_leaking_paths(qtbot) -> None:
    library = FlakyLibrary()
    window = MainWindow(project_library_service=library)
    qtbot.addWidget(window)
    window.configure_production_shell()
    window.show_project_hub()

    assert window.fixture_code == "REAL_PROJECT_HUB_UNAVAILABLE"
    assert window._nav_buttons["Beranda"].isChecked()
    assert "DAFTAR PROJECT BELUM DAPAT DIPERIKSA" in _text(window)
    assert "BUKAN berarti tidak ada proyek" in _text(window)
    assert "PRIVATE_DISK_LOCATION" not in _text(window)
    assert window._status_project.text() == "Status project tidak diketahui"

    retry = window.findChild(QPushButton, "RealProjectHubRetry")
    assert retry is not None and retry.isEnabled()
    library.fail = False
    retry.click()
    assert library.calls == 2
    assert window.fixture_code == "REAL_PROJECT_HUB"
    assert "0 project" in window._status_project.text()
    window.close()


def test_missing_library_disables_retry_and_exposes_safe_diagnostics(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.configure_production_shell()
    window.show_project_hub()

    assert window.fixture_code == "REAL_PROJECT_HUB_UNAVAILABLE"
    retry = window.findChild(QPushButton, "RealProjectHubRetry")
    assert retry is not None and not retry.isEnabled()
    assert "belum dikonfigurasi" in retry.toolTip()
    diag = window.findChild(QPushButton, "RealProjectHubOpenDiagnostics")
    assert diag is not None and diag.isEnabled()
    diag.click()
    assert window.fixture_code == "REAL_DIAGNOSTICS"
    assert window._last_diagnostics_snapshot is not None
    assert window._last_diagnostics_snapshot.recent_project_count is None
    window.close()


def test_nonproduction_reference_still_uses_approved_empty_fixture(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show_project_hub()
    assert window.fixture_code == "UI-IMG-001A"
    assert window.findChild(QPushButton, "RealProjectHubRetry") is None
    window.close()
