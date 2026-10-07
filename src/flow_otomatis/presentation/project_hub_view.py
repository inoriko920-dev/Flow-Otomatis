"""Real local Project Hub rendered with the frozen STEP 09 compositions."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QTableWidgetItem, QWidget

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
    on_open: Callable[[str], object],
    on_import: Callable[[], object],
) -> QWidget:
    """Render local recent projects without changing frozen Project Hub layout."""

    code = "UI-IMG-001B" if workspaces else "UI-IMG-001A"
    root = build_screen(get_fixture(code))

    import_button = _button(root, "Impor Paket Episode")
    if import_button is not None:
        import_button.clicked.connect(on_import)

    if not workspaces:
        return root

    table = _project_table(root)
    table.setRowCount(len(workspaces))
    for row, workspace in enumerate(workspaces):
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

    def open_row(row: int, _column: int) -> None:
        if 0 <= row < len(workspaces):
            on_open(workspaces[row].episode_id)

    table.cellDoubleClicked.connect(open_row)
    table.setCurrentCell(0, 0)

    open_button = _button(root, "Buka Project")
    if open_button is not None:
        open_button.clicked.connect(lambda: on_open(workspaces[0].episode_id))

    for label in root.findChildren(QLabel):
        if label.text() == "Project dapat dipulihkan":
            label.setText(f"{len(workspaces)} project lokal siap dibuka kembali")
        elif label.text().startswith("Snapshot lokal EP001"):
            label.setText(
                "Workspace SQLite tersimpan ditemukan. Buka kembali untuk melanjutkan "
                "Scene planning dari state terakhir."
            )
        elif label.text() == "1 project":
            label.setText(f"{len(workspaces)} project")
    return root
