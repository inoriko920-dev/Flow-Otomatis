from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from flow_otomatis.application.services import ProjectLibraryService
from flow_otomatis.domain.errors import WorkspaceCorruptError
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


def _db_path(root: Path, episode_id: str) -> Path:
    return root / episode_id / "project.sqlite3"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_corrupt_project_is_isolated_and_read_does_not_mutate_source(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    repository = SqliteWorkspaceRepository(projects_root)
    now = datetime.now(UTC)
    healthy = _workspace("EP102_HEALTHY", now)
    corrupt = _workspace("EP103_CORRUPT", now - timedelta(minutes=1))
    repository.save(healthy)
    repository.save(corrupt)

    corrupt_db = _db_path(projects_root, corrupt.episode_id)
    with sqlite3.connect(corrupt_db) as connection:
        connection.execute("UPDATE scenes SET readiness = 'INVALID_ENUM'")
        connection.commit()
    before = _sha256(corrupt_db)

    service = ProjectLibraryService(repository)
    scan = service.scan_recent()

    assert [item.episode_id for item in scan.workspaces] == ["EP102_HEALTHY"]
    assert [(item.episode_id, item.kind) for item in scan.issues] == [
        ("EP103_CORRUPT", "CORRUPT")
    ]
    assert [item.episode_id for item in service.list_recent()] == ["EP102_HEALTHY"]
    assert service.open_project("EP102_HEALTHY") == healthy
    with pytest.raises(WorkspaceCorruptError):
        service.open_project("EP103_CORRUPT")
    assert _sha256(corrupt_db) == before


@pytest.mark.parametrize(
    ("column", "bad_value"),
    [
        ("imported_at", "not-a-timestamp"),
        ("target_duration_s", "not-a-number"),
    ],
)
def test_invalid_persisted_types_raise_typed_corruption_without_repair(
    tmp_path: Path,
    column: str,
    bad_value: str,
) -> None:
    projects_root = tmp_path / "projects"
    repository = SqliteWorkspaceRepository(projects_root)
    episode_id = f"EP104_{column.upper()}"
    repository.save(_workspace(episode_id, datetime.now(UTC)))
    db_path = _db_path(projects_root, episode_id)

    table = "project" if column == "imported_at" else "scenes"
    with sqlite3.connect(db_path) as connection:
        connection.execute(f"UPDATE {table} SET {column} = ?", (bad_value,))
        connection.commit()
    before = _sha256(db_path)

    with pytest.raises(WorkspaceCorruptError):
        repository.load(episode_id)

    scan = repository.scan_recent()
    assert scan.workspaces == ()
    assert [(item.episode_id, item.kind) for item in scan.issues] == [
        (episode_id, "CORRUPT")
    ]
    assert _sha256(db_path) == before
