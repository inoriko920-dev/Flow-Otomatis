"""Real, local-only diagnostics presented in the approved frozen Diagnostik layout.

The original reference screenshots are never changed. This view deliberately
does not include provider logs, tokens, profile identifiers or remote claims.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QTableWidgetItem, QWidget

from flow_otomatis.presentation.fixtures import get_fixture
from flow_otomatis.presentation.screen_factory import build_screen


@dataclass(frozen=True, slots=True)
class LocalDiagnosticSnapshot:
    """Sanitized facts known to the running desktop process, not Google Flow."""

    recent_project_count: int | None
    recent_project_issue_count: int | None
    active_scene_count: int | None

    def as_report(self) -> dict[str, object]:
        """Whitelist-only report: no filesystem paths, project IDs or credentials."""

        return {
            "schema_version": "1.0",
            "source": "LOCAL_APPLICATION_ONLY",
            "recent_scan_limit": 10,
            "recent_project_count": self.recent_project_count,
            "recent_project_issue_count": self.recent_project_issue_count,
            "active_scene_count": self.active_scene_count,
            "flow_access": "NOT_VERIFIED",
            "live_generate": "DISABLED",
            "includes_secrets": False,
            "includes_profile_identifiers": False,
            "includes_project_identifiers": False,
        }


def build_local_diagnostics_view(
    snapshot: LocalDiagnosticSnapshot,
    *,
    on_refresh: Callable[[], object],
    on_export: Callable[[], object],
) -> QWidget:
    """Replace frozen fake events with truthful, read-only local status rows."""

    root = build_screen(get_fixture("UI-IMG-008A"))
    root.setObjectName("RealLocalDiagnostics")
    table = next(
        (table for table in root.findChildren(QTableWidget) if table.columnCount() == 5),
        None,
    )
    if table is None:
        raise RuntimeError("Approved diagnostics layout lacks five-column table")

    table.setObjectName("RealLocalDiagnosticsTable")
    table.setHorizontalHeaderLabels(("Waktu", "Terkait", "Pesan", "Stage", "Status"))
    project_state = (
        f"{snapshot.recent_project_count} project siap • "
        f"{snapshot.recent_project_issue_count} bermasalah"
        if snapshot.recent_project_count is not None
        and snapshot.recent_project_issue_count is not None
        else "Belum dapat diperiksa"
    )
    scene_state = (
        f"{snapshot.active_scene_count} Scene dimuat"
        if snapshot.active_scene_count is not None
        else "Belum ada Workspace aktif"
    )
    rows = (
        ("—", "Project lokal", project_state, "Local", "Info"),
        ("—", "Workspace lokal", scene_state, "Local", "Info"),
        ("—", "Google Flow", "Akses akun dan workspace belum diverifikasi", "Provider", "Belum"),
        ("—", "Generate", "Generate live belum diaktifkan", "Provider", "Diblokir"),
        ("—", "Diagnostik", "Tidak melakukan koneksi atau operasi berbayar", "Local", "Aman"),
    )
    table.setRowCount(len(rows))
    for row_index, values in enumerate(rows):
        for col_index, value in enumerate(values):
            table.setItem(row_index, col_index, QTableWidgetItem(value))
    table.clearSelection()

    for button in root.findChildren(QPushButton):
        if button.text() == "Refresh":
            button.setObjectName("RealDiagnosticsRefresh")
            button.clicked.connect(on_refresh)
        elif button.text() == "Export Diagnostik Tersamarkan":
            button.setObjectName("RealDiagnosticsExport")
            button.clicked.connect(on_export)

    # Replace frozen fake Agent-log copy in the production-only view.
    for label in root.findChildren(QLabel):
        if label.text() == "AI Agent tidak melakukan retry otomatis":
            label.setText("DIAGNOSTIK LOKAL • BUKAN STATUS GOOGLE FLOW")
        elif label.text().startswith("Agent dapat mengusulkan retry."):
            label.setText(
                "Menampilkan fakta dari proses aplikasi dan database lokal saja. "
                "Tidak membaca credential, cookie, atau saldo Google. "
                "Status Google Flow perlu verifikasi terpisah."
            )
    return root
