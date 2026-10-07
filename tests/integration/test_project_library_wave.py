from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from flow_otomatis.application.services import ProjectLibraryService
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.persistence import SqliteWorkspaceRepository


def _workspace(episode_id: str, imported_at: datetime) -> WorkspaceState:
    scene = WorkspaceScene(
        scene_id="SCENE_001",
        image_file="image.png",
        image_exists=True,
        motion_prompt="Move slowly.",
        target_duration_s=3.0,
        recommended_flow_duration_s=4,
        selected_flow_duration_s=4,
        readiness=SceneReadiness.READY,
        trim_target_s=3.0,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
    )
    return WorkspaceState(
        schema_version="1.0",
        episode_id=episode_id,
        project_name=f"Project {episode_id}",
        source_package_path=str(Path("package.zip")),
        created_at=imported_at,
        imported_at=imported_at,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(scene,),
    )


def test_project_library_lists_newest_and_reopens_persisted_state(tmp_path: Path) -> None:
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    now = datetime.now(UTC)
    older = _workspace("EP100_OLDER", now - timedelta(minutes=10))
    newer = _workspace("EP101_NEWER", now)
    repository.save(older)
    repository.save(newer)
    service = ProjectLibraryService(repository)

    recent = service.list_recent()

    assert [item.episode_id for item in recent] == ["EP101_NEWER", "EP100_OLDER"]
    assert service.open_project("EP100_OLDER") == older
