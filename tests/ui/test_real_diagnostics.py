"""Real Diagnostik navigation must not display synthetic provider history."""

from __future__ import annotations

import json
from types import SimpleNamespace

from PySide6.QtWidgets import QFileDialog, QMessageBox, QPushButton, QTableWidget

from flow_otomatis.presentation.main_window import MainWindow


class LocalProjects:
    def __init__(self) -> None:
        self.projects = 1
        self.issues = 0
        self.fail = False
        self.calls = 0

    def scan_recent(self, limit: int = 10) -> SimpleNamespace:
        assert limit == 10
        self.calls += 1
        if self.fail:
            raise OSError("secret-home/projects/one: database readonly")
        return SimpleNamespace(
            workspaces=tuple(object() for _ in range(self.projects)),
            issues=tuple(object() for _ in range(self.issues)),
        )


def _diagnostics_table(window: MainWindow) -> QTableWidget:
    table = window.findChild(QTableWidget, "RealLocalDiagnosticsTable")
    assert table is not None
    return table


def test_real_diagnostics_uses_local_fact_rows_and_manual_refresh(qtbot) -> None:
    projects = LocalProjects()
    window = MainWindow(project_library_service=projects)
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Diagnostik")

    assert window.fixture_code == "REAL_DIAGNOSTICS"
    table = _diagnostics_table(window)
    assert table.rowCount() == 5
    assert "1 project siap" in table.item(0, 2).text()
    assert "Belum ada Workspace aktif" in table.item(1, 2).text()
    assert "belum diverifikasi" in table.item(2, 2).text()
    assert "belum diaktifkan" in table.item(3, 2).text()
    assert "Download selesai" not in "\\n".join(
        table.item(row, 2).text() for row in range(table.rowCount())
    )
    assert projects.calls == 1

    projects.projects = 2
    projects.issues = 1
    refresh = window.findChild(QPushButton, "RealDiagnosticsRefresh")
    assert refresh is not None and refresh.isEnabled()
    refresh.click()
    assert projects.calls == 2
    assert "2 project siap • 1 bermasalah" in _diagnostics_table(window).item(0, 2).text()
    assert window._connection_badge.text() == "●  Mode Lokal"
    window.close()


def test_diagnostics_json_export_is_whitelist_only_and_no_overwrite(
    qtbot, monkeypatch, tmp_path
) -> None:
    projects = LocalProjects()
    window = MainWindow(project_library_service=projects)
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Diagnostik")

    outfile = tmp_path / "diagnostik_lokal.json"
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda *_args, **_kwargs: (str(outfile), "JSON")
    )
    export = window.findChild(QPushButton, "RealDiagnosticsExport")
    assert export is not None
    export.click()
    report = json.loads(outfile.read_text(encoding="utf-8"))
    assert report == {
        "schema_version": "1.0",
        "source": "LOCAL_APPLICATION_ONLY",
        "recent_scan_limit": 10,
        "recent_project_count": 1,
        "recent_project_issue_count": 0,
        "active_scene_count": None,
        "flow_access": "NOT_VERIFIED",
        "live_generate": "DISABLED",
        "includes_secrets": False,
        "includes_profile_identifiers": False,
        "includes_project_identifiers": False,
    }
    assert "secret" not in outfile.read_text(encoding="utf-8").lower()
    warnings: list[str] = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda _parent, title, _message: warnings.append(title),
    )
    export.click()
    assert warnings == ["File sudah ada"]
    assert json.loads(outfile.read_text(encoding="utf-8")) == report
    window.close()


def test_diagnostics_fails_closed_without_project_reader(qtbot) -> None:
    projects = LocalProjects()
    projects.fail = True
    window = MainWindow(project_library_service=projects)
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Diagnostik")
    table = _diagnostics_table(window)
    assert "Belum dapat diperiksa" in table.item(0, 2).text()
    assert "secret-home" not in " ".join(
        table.item(r, c).text()
        for r in range(table.rowCount())
        for c in range(table.columnCount())
    )
    report = window._last_diagnostics_snapshot
    assert report is not None
    assert report.as_report()["recent_project_count"] is None
    window.close()


def test_frozen_diagnostics_route_stays_original_for_reference_mode(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._open_navigation_item("Diagnostik")
    assert window.fixture_code == "UI-IMG-008A"
    assert window.findChild(QTableWidget, "RealLocalDiagnosticsTable") is None
    # Pixel-perfect STEP09 screenshot fixture is not repainted.
    window.close()
