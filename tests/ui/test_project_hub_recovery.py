from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QTableWidget

from flow_otomatis.application.services import ProjectLibraryService
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.persistence import SqliteWorkspaceRepository
from flow_otomatis.presentation.main_window import MainWindow


def _workspace(
    episode_id: str = "EP200_RECOVERY",
    project_name: str = "Recovered Biography",
) -> WorkspaceState:
    scene = WorkspaceScene(
        scene_id="SCENE_016",
        image_file="image.png",
        image_exists=True,
        motion_prompt="Recovered prompt.",
        target_duration_s=7.32,
        recommended_flow_duration_s=8,
        selected_flow_duration_s=8,
        readiness=SceneReadiness.READY,
        trim_target_s=7.32,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
    )
    now = datetime.now(UTC)
    return WorkspaceState(
        schema_version="1.0",
        episode_id=episode_id,
        project_name=project_name,
        source_package_path=str(Path("episode.zip")),
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(scene,),
    )


def _visible_text(window: MainWindow) -> str:
    text = [label.text() for label in window.findChildren(QLabel)]
    for table in window.findChildren(QTableWidget):
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None:
                    text.append(item.text())
    return "\n".join(text)


def test_real_project_hub_opens_persisted_workspace(tmp_path: Path, qtbot) -> None:
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    repository.save(_workspace())
    library = ProjectLibraryService(repository)
    window = MainWindow(project_library_service=library)
    qtbot.addWidget(window)

    window.show_project_hub()
    hub_text = _visible_text(window)
    assert window.fixture_code == "REAL_PROJECT_HUB"
    assert "Recovered Biography" in hub_text
    assert "EP200_RECOVERY" in hub_text

    open_button = next(
        button for button in window.findChildren(QPushButton) if button.text() == "Buka Project"
    )
    qtbot.mouseClick(open_button, Qt.MouseButton.LeftButton)

    assert window.fixture_code == "REAL_WORKSPACE"
    assert window.current_workspace is not None
    assert window.current_workspace.episode_id == "EP200_RECOVERY"
    assert "Recovered prompt." in _visible_text(window)


def test_project_hub_surfaces_corruption_and_keeps_healthy_project_openable(
    tmp_path: Path,
    qtbot,
    monkeypatch,
) -> None:
    projects_root = tmp_path / "projects"
    repository = SqliteWorkspaceRepository(projects_root)
    healthy = _workspace("EP201_HEALTHY", "Healthy Biography")
    corrupt = _workspace("EP202_CORRUPT", "Corrupt Biography")
    repository.save(healthy)
    repository.save(corrupt)

    corrupt_db = projects_root / corrupt.episode_id / "project.sqlite3"
    with sqlite3.connect(corrupt_db) as connection:
        connection.execute("UPDATE scenes SET readiness = 'INVALID_ENUM'")
        connection.commit()
    before = hashlib.sha256(corrupt_db.read_bytes()).hexdigest()

    warnings: list[tuple[str, str]] = []

    def capture_warning(_parent, title: str, message: str):
        warnings.append((title, message))
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "warning", capture_warning)

    library = ProjectLibraryService(repository)
    window = MainWindow(project_library_service=library)
    qtbot.addWidget(window)
    window.show_project_hub()

    hub_text = _visible_text(window)
    assert "Healthy Biography" in hub_text
    assert "EP201_HEALTHY" in hub_text
    assert "EP202_CORRUPT" in hub_text
    assert "Data Rusak" in hub_text
    assert "1 project siap • 1 project bermasalah" in hub_text

    table = next(table for table in window.findChildren(QTableWidget) if table.columnCount() == 5)
    corrupt_row = next(
        row
        for row in range(table.rowCount())
        if table.item(row, 1) is not None and table.item(row, 1).text() == "EP202_CORRUPT"
    )
    table.setCurrentCell(corrupt_row, 0)
    open_button = next(
        button for button in window.findChildren(QPushButton) if button.text() == "Buka Project"
    )
    qtbot.mouseClick(open_button, Qt.MouseButton.LeftButton)

    assert window.fixture_code == "REAL_PROJECT_HUB"
    assert warnings
    assert warnings[-1][0] == "Project Data Rusak"
    assert "File project tidak diubah" in warnings[-1][1]
    assert hashlib.sha256(corrupt_db.read_bytes()).hexdigest() == before

    healthy_row = next(
        row
        for row in range(table.rowCount())
        if table.item(row, 1) is not None and table.item(row, 1).text() == "EP201_HEALTHY"
    )
    table.setCurrentCell(healthy_row, 0)
    qtbot.mouseClick(open_button, Qt.MouseButton.LeftButton)

    assert window.fixture_code == "REAL_WORKSPACE"
    assert window.current_workspace is not None
    assert window.current_workspace.episode_id == "EP201_HEALTHY"
