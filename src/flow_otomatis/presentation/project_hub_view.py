"""Real local Project Hub rendered with the frozen STEP 09 compositions."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QTableWidgetItem, QWidget

from flow_otomatis.application.ports.workspace_repository import WorkspaceReadIssue
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.presentation.fixtures import get_fixture
from flow_otomatis.presentation.screen_factory import build_screen


def _project_table(root: QWidget) -> QTableWidget:
    for table in root.findChildren(QTableWidget):
        if table.columnCount() == 5:
            return table
    raise RuntimeError("Frozen Project Hub is missing the recent-project table")


def _button(root: QWidget, text: str) -> QPushButton | None:
    for button in root.findChildren(QPushButton):
        if button.text() == text:
            return button
    return None


def build_project_hub_view(
    workspaces: Sequence[WorkspaceState],
    *,
    issues: Sequence[WorkspaceReadIssue] = (),
    on_open: Callable[[str], object],
    on_import: Callable[[], object],
) -> QWidget:
    """Render healthy and isolated unreadable projects in the frozen layout."""

    total_entries = len(workspaces) + len(issues)
    code = "UI-IMG-001B" if total_entries else "UI-IMG-001A"
    root = build_screen(get_fixture(code))

    import_button = _button(root, "Impor Paket Episode")
    if import_button is not None:
        import_button.clicked.connect(on_import)

    if not total_entries:
        return root

    table = _project_table(root)
    table.setRowCount(total_entries)
    episode_ids: list[str] = []

    for row, workspace in enumerate(workspaces):
        episode_ids.append(workspace.episode_id)
        status = (
            "Siap"
            if workspace.blocking_count == 0 and workspace.duration_selection_count == 0
            else "Perlu dilanjutkan"
        )
        values = (
            workspace.project_name,
            workspace.episode_id,
            str(len(workspace.scenes)),
            status,
            workspace.imported_at.astimezone().strftime("%Y-%m-%d %H:%M"),
        )
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(value))

    for offset, issue in enumerate(issues):
        row = len(workspaces) + offset
        episode_ids.append(issue.episode_id)
        is_corrupt = issue.kind == "CORRUPT"
        values = (
            "Project data rusak" if is_corrupt else "Project tidak dapat dibaca",
            issue.episode_id,
            "—",
            "Data Rusak" if is_corrupt else "Tidak Tersedia",
            "—",
        )
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(value))

    def open_row(row: int, _column: int = 0) -> None:
        if 0 <= row < len(episode_ids):
            on_open(episode_ids[row])

    table.cellDoubleClicked.connect(open_row)
    table.setCurrentCell(0, 0)

    open_button = _button(root, "Buka Project")
    if open_button is not None:
        open_button.clicked.connect(lambda: open_row(table.currentRow()))

    for label in root.findChildren(QLabel):
        if label.text() == "Project dapat dipulihkan":
            if issues:
                label.setText(
                    f"{len(workspaces)} project siap • {len(issues)} project bermasalah"
                )
            else:
                label.setText(f"{len(workspaces)} project lokal siap dibuka kembali")
        elif label.text().startswith("Snapshot lokal EP001"):
            if issues:
                label.setText(
                    "Project bermasalah diisolasi dan tidak diubah. "
                    "Project sehat tetap dapat dibuka."
                )
            else:
                label.setText(
                    "Workspace SQLite tersimpan ditemukan. Buka kembali untuk melanjutkan "
                    "Scene planning dari state terakhir."
                )
        elif label.text() == "1 project":
            label.setText(f"{total_entries} project")
    return root
