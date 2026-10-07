from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget

from flow_otomatis.application.services import LocalResultsService
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.filesystem import ResultManifestWriter
from flow_otomatis.infrastructure.persistence import (
    SqliteDownloadResultRepository,
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)
from flow_otomatis.presentation.main_window import MainWindow


def _visible_text(window: MainWindow) -> str:
    values = [label.text() for label in window.findChildren(QLabel)]
    for table in window.findChildren(QTableWidget):
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None:
                    values.append(item.text())
    return "\n".join(values)


def test_real_hasil_view_exports_handoff_manifest(tmp_path: Path, qtbot) -> None:
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    job_repo = SqliteGenerationJobRepository(projects_root)
    download_repo = SqliteDownloadResultRepository(projects_root)
    writer = ResultManifestWriter(projects_root)
    service = LocalResultsService(workspace_repo, job_repo, download_repo, writer)

    now = datetime.now(UTC)
    scene = WorkspaceScene(
        scene_id="SCENE_001",
        image_file="SCENE_001.png",
        image_exists=True,
        motion_prompt="Slow push-in.",
        target_duration_s=3.8,
        recommended_flow_duration_s=4,
        selected_flow_duration_s=4,
        readiness=SceneReadiness.READY,
        trim_target_s=3.8,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
    )
    workspace = WorkspaceState(
        schema_version="1.0",
        episode_id="EP401_RESULTS_UI",
        project_name="Results UI Test",
        source_package_path=str(Path("package.zip")),
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(scene,),
    )
    workspace_repo.save(workspace)
    job = GenerationJob(
        job_id="EP401_RESULTS_UI:SCENE_001:GENERATE",
        episode_id="EP401_RESULTS_UI",
        scene_id="SCENE_001",
        target_duration_s=3.8,
        flow_duration_s=4,
        state=GenerationJobState.QUEUED,
        created_at=now,
        updated_at=now,
    )
    job_repo.ensure_jobs((job,))
    claimed = job_repo.claim_next(workspace.episode_id)
    assert claimed is not None
    job_repo.mark_generated(job.job_id, "fake:SCENE_001")
    output = tmp_path / "SCENE_001.mp4"
    output.write_bytes(b"synthetic-video")
    service.record_downloaded(workspace.episode_id, scene.scene_id, str(output))

    window = MainWindow(local_results_service=service)
    qtbot.addWidget(window)
    window.show_workspace_state(workspace)
    window.show_results_state()

    text = _visible_text(window)
    assert window.fixture_code == "REAL_RESULTS"
    assert "S001" in text
    assert "Selesai" in text
    assert "Tersimpan" in text
    assert "SCENE_001.mp4" in text

    button = next(
        item
        for item in window.findChildren(QPushButton)
        if item.text() == "Tandai Siap untuk Editing"
    )
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert window.last_result_manifest_path is not None
    assert window.last_result_manifest_path.is_file()
