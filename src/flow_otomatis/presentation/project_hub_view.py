"""Real local Project Hub rendered with the frozen STEP 09 compositions."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

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
    on_preview_ui: Callable[[], object] | None = None,
    import_available: bool = True,
) -> QWidget:
    """Render healthy and isolated unreadable projects in the frozen layout."""

    total_entries = len(workspaces) + len(issues)
    code = "UI-IMG-001B" if total_entries else "UI-IMG-001A"
    root = build_screen(get_fixture(code))

    import_button = _button(root, "Impor Paket Episode")
    if import_button is not None:
        import_button.setEnabled(import_available)
        if import_available:
            import_button.clicked.connect(on_import)
        else:
            import_button.setToolTip("Layanan impor paket episode belum tersedia.")
        if on_preview_ui is not None:
            actions = import_button.parentWidget()
            actions_layout = actions.layout() if actions is not None else None
            if isinstance(actions_layout, QHBoxLayout):
                preview_button = QPushButton("Lihat 22 Desain UI Baru")
                preview_button.setObjectName("ProjectHubUix22Preview")
                preview_button.setToolTip(
                    "Buka 22 desain UI yang telah disetujui. Mode simulasi, "
                    "tanpa login atau Generate; tidak memerlukan project."
                )
                preview_button.clicked.connect(on_preview_ui)
                actions_layout.insertWidget(1, preview_button)

    create_button = _button(root, "Buat Project")
    if create_button is not None:
        # There is no second/empty project-creation path: a valid package
        # is required to establish real persisted Workspace/Scene records.
        create_button.setText("Buat Project dari Paket")
        create_button.setObjectName("ProjectHubCreateFromPackage")
        create_button.setEnabled(import_available)
        if import_available:
            create_button.clicked.connect(on_import)
        else:
            create_button.setToolTip("Impor paket harus tersedia untuk membuat project.")

    open_button = _button(root, "Buka Project")
    if open_button is not None:
        open_button.setObjectName("ProjectHubOpenProject")
        open_button.setEnabled(bool(total_entries))
        if not total_entries:
            open_button.setToolTip("Belum ada project lokal yang bisa dibuka.")

    if not total_entries:
        for label in root.findChildren(QLabel):
            if "buat project baru, atau buka project" in label.text():
                label.setText(
                    "Impor paket episode untuk membuat Workspace pertama. "
                    "Project tersimpan akan muncul di daftar ini."
                )
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

    if open_button is not None:
        open_button.clicked.connect(lambda: open_row(table.currentRow()))

    for label in root.findChildren(QLabel):
        if label.text() == "Project dapat dipulihkan":
            if issues:
                label.setText(f"{len(workspaces)} project siap • {len(issues)} project bermasalah")
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
