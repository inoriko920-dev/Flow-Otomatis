"""F05: reading local Generation history is never an implicit migration."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from flow_otomatis.domain.errors import StorageError
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.persistence import (
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)


def _setup(tmp_path: Path) -> tuple[Path, SqliteGenerationJobRepository]:
    root = tmp_path / "projects"
    now = datetime.now(UTC)
    scene = WorkspaceScene(
        scene_id="SCENE_001",
        image_file="image.png",
        image_exists=True,
        motion_prompt="Pan slowly",
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
        episode_id="EP800_READ_ONLY",
        project_name="Historical DB",
        source_package_path="package.zip",
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(scene,),
    )
    SqliteWorkspaceRepository(root).save(workspace)
    return root / "EP800_READ_ONLY" / "project.sqlite3", SqliteGenerationJobRepository(root)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _job() -> GenerationJob:
    now = datetime.now(UTC)
    return GenerationJob(
        job_id="EP800_READ_ONLY:SCENE_001:GENERATE",
        episode_id="EP800_READ_ONLY",
        scene_id="SCENE_001",
        target_duration_s=3.8,
        flow_duration_s=4,
        state=GenerationJobState.QUEUED,
        created_at=now,
        updated_at=now,
        image_file="image.png",
        motion_prompt="Pan slowly",
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        request_fingerprint="test-request-revision",
    )


def test_t14_legacy_project_list_does_not_create_schema_or_journal(tmp_path: Path) -> None:
    db, repo = _setup(tmp_path)
    before = _digest(db)
    assert repo.list_for_episode("EP800_READ_ONLY") == ()
    assert _digest(db) == before
    with sqlite3.connect(db) as connection:
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name LIKE 'generation_%'"
            ).fetchall()
            == []
        )
    assert not Path(str(db) + "-journal").exists()
    assert not Path(str(db) + "-wal").exists()


def test_t15_read_existing_jobs_does_not_write(tmp_path: Path) -> None:
    db, repo = _setup(tmp_path)
    repo.prepare_jobs((_job(),))
    before = _digest(db)
    jobs = repo.list_for_episode("EP800_READ_ONLY")
    assert len(jobs) == 1
    assert jobs[0].scene_id == "SCENE_001"
    assert _digest(db) == before


def test_t16_future_schema_is_rejected_without_read_or_write_changes(tmp_path: Path) -> None:
    db, repo = _setup(tmp_path)
    repo.prepare_jobs((_job(),))
    with sqlite3.connect(db) as connection:
        connection.execute("UPDATE generation_job_schema SET schema_version = 99")
    before = _digest(db)
    with pytest.raises(StorageError, match="Unsupported"):
        repo.list_for_episode("EP800_READ_ONLY")
    assert _digest(db) == before
    with pytest.raises(StorageError, match="Unsupported"):
        repo.prepare_jobs((_job(),))
    assert _digest(db) == before


def test_t17_explicit_write_migrates_legacy_history(tmp_path: Path) -> None:
    db, repo = _setup(tmp_path)
    with sqlite3.connect(db) as connection:
        connection.execute(
            """CREATE TABLE generation_jobs (
                job_id TEXT PRIMARY KEY, episode_id TEXT NOT NULL,
                scene_id TEXT NOT NULL, target_duration_s REAL NOT NULL,
                flow_duration_s INTEGER NOT NULL, state TEXT NOT NULL,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                remote_result_id TEXT, error_message TEXT,
                UNIQUE(episode_id, scene_id)
            )"""
        )
        job = _job()
        connection.execute(
            """INSERT INTO generation_jobs
            (job_id, episode_id, scene_id, target_duration_s, flow_duration_s,
             state, created_at, updated_at, remote_result_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job.job_id,
                job.episode_id,
                job.scene_id,
                job.target_duration_s,
                job.flow_duration_s,
                "GENERATED",
                job.created_at.isoformat(),
                job.updated_at.isoformat(),
                "remote:historical",
            ),
        )
    before = _digest(db)
    old = repo.list_for_episode("EP800_READ_ONLY")
    assert len(old) == 1 and old[0].remote_result_id == "remote:historical"
    assert _digest(db) == before
    repo.prepare_jobs((_job(),))
    assert repo.list_for_episode("EP800_READ_ONLY")[0].remote_result_id == "remote:historical"
    with sqlite3.connect(db) as connection:
        assert connection.execute(
            "SELECT schema_version FROM generation_job_schema"
        ).fetchone() == (2,)


def test_t17_failed_explicit_schema_migration_rolls_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db, repo = _setup(tmp_path)
    before = _digest(db)

    def fail_during_migration(connection: sqlite3.Connection) -> None:
        # Called after the version marker was created, before COMMIT.
        assert connection.execute(
            "SELECT 1 FROM sqlite_master WHERE name = 'generation_job_schema'"
        ).fetchone()
        raise sqlite3.OperationalError("synthetic migration fault")

    monkeypatch.setattr(repo, "_create_latest_table", fail_during_migration)
    with pytest.raises(StorageError, match="Could not prepare"):
        repo.prepare_jobs((_job(),))

    with sqlite3.connect(db) as connection:
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE name LIKE 'generation_%'"
        ).fetchall() == []
    assert _digest(db) == before
