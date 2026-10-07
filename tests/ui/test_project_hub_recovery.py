from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget

from flow_otomatis.application.services import ProjectLibraryService
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.persistence import SqliteWorkspaceRepository
from flow_otomatis.presentation.main_window import MainWindow


def _workspace() -> WorkspaceState:
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
        episode_id="EP200_RECOVERY",
        project_name="Recovered Biography",
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
