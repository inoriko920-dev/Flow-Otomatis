from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from flow_otomatis.application.services import LocalResultsService
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.result import DownloadRecord, DownloadState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.filesystem import ResultManifestWriter
from flow_otomatis.infrastructure.persistence import (
    SqliteDownloadResultRepository,
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)


def _workspace() -> WorkspaceState:
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
    return WorkspaceState(
        schema_version="1.0",
        episode_id="EP400_RESULTS",
        project_name="Results Test",
        source_package_path=str(Path("package.zip")),
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(scene,),
    )


def _service(
    tmp_path: Path,
) -> tuple[
    LocalResultsService,
    SqliteGenerationJobRepository,
]:
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace = _workspace()
    workspace_repo.save(workspace)
    job_repo = SqliteGenerationJobRepository(projects_root)
    download_repo = SqliteDownloadResultRepository(projects_root)
    writer = ResultManifestWriter(projects_root)
    service = LocalResultsService(workspace_repo, job_repo, download_repo, writer)
    return service, job_repo


def _queue_one(job_repo: SqliteGenerationJobRepository) -> GenerationJob:
    now = datetime.now(UTC)
    job = GenerationJob(
        job_id="EP400_RESULTS:SCENE_001:GENERATE",
        episode_id="EP400_RESULTS",
        scene_id="SCENE_001",
        target_duration_s=3.8,
        flow_duration_s=4,
        state=GenerationJobState.QUEUED,
        created_at=now,
        updated_at=now,
        image_file="SCENE_001.png",
        motion_prompt="Slow push-in.",
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        request_fingerprint="verified-results-fixture",
    )
    job_repo.ensure_jobs((job,))
    return job


def test_generate_download_and_handoff_manifest_remain_separate(tmp_path: Path) -> None:
    service, job_repo = _service(tmp_path)
    job = _queue_one(job_repo)
    claimed = job_repo.claim_next(
        "EP400_RESULTS",
        "results-owner",
        lease_seconds=60,
    )
    assert claimed is not None
    job_repo.mark_generated(job.job_id, "fake:SCENE_001", "results-owner")

    before_download = service.snapshot("EP400_RESULTS")
    assert before_download.generated_count == 1
    assert before_download.downloaded_count == 0
    assert before_download.handoff_ready is False

    output = tmp_path / "SCENE_001.mp4"
    output.write_bytes(b"synthetic-video")
    service.record_downloaded("EP400_RESULTS", "SCENE_001", str(output))

    after_download = service.snapshot("EP400_RESULTS")
    assert after_download.generated_count == 1
    assert after_download.downloaded_count == 1
    assert after_download.scenes[0].download_state == DownloadState.DOWNLOADED
    assert after_download.handoff_ready is True

    manifest_path = service.export_manifest("EP400_RESULTS")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["episode_id"] == "EP400_RESULTS"
    assert payload["scenes"][0]["generate_status"] == "GENERATED"
    assert payload["scenes"][0]["download_status"] == "DOWNLOADED"
    manifest_text = manifest_path.read_text(encoding="utf-8").lower()
    assert "credential" not in manifest_text
    assert "cookie" not in manifest_text
    assert "token" not in manifest_text


def test_download_success_requires_generated_job(tmp_path: Path) -> None:
    service, job_repo = _service(tmp_path)
    _queue_one(job_repo)
    output = tmp_path / "SCENE_001.mp4"
    output.write_bytes(b"synthetic-video")

    with pytest.raises(InternalInvariantError):
        service.record_downloaded("EP400_RESULTS", "SCENE_001", str(output))

def test_migration_preserves_generated_result_and_existing_download(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace = _workspace()
    workspace_repo.save(workspace)
    db_path = projects_root / workspace.episode_id / "project.sqlite3"
    now = datetime(2026, 10, 7, 15, 0, tzinfo=UTC)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE generation_jobs (
                job_id TEXT PRIMARY KEY,
                episode_id TEXT NOT NULL,
                scene_id TEXT NOT NULL,
                target_duration_s REAL NOT NULL,
                flow_duration_s INTEGER NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                remote_result_id TEXT,
                error_message TEXT,
                UNIQUE (episode_id, scene_id)
            )
            """
        )
        connection.execute(
            """
            INSERT INTO generation_jobs (
                job_id, episode_id, scene_id, target_duration_s,
                flow_duration_s, state, created_at, updated_at,
                remote_result_id, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                "EP400_RESULTS:SCENE_001:GENERATE",
                "EP400_RESULTS",
                "SCENE_001",
                3.8,
                4,
                GenerationJobState.GENERATED.value,
                now.isoformat(),
                now.isoformat(),
                "remote:kept",
            ),
        )
        connection.commit()

    output = tmp_path / "already-downloaded.mp4"
    output.write_bytes(b"existing-result")
    download_repo = SqliteDownloadResultRepository(projects_root)
    download_repo.save(
        DownloadRecord(
            episode_id="EP400_RESULTS",
            scene_id="SCENE_001",
            state=DownloadState.DOWNLOADED,
            updated_at=now,
            output_path=str(output.resolve()),
            take=1,
        )
    )

    job_repo = SqliteGenerationJobRepository(projects_root)
    writer = ResultManifestWriter(projects_root)
    service = LocalResultsService(workspace_repo, job_repo, download_repo, writer)

    snapshot = service.snapshot("EP400_RESULTS")
    migrated = job_repo.list_for_episode("EP400_RESULTS")

    assert migrated[0].state is GenerationJobState.GENERATED
    assert migrated[0].remote_result_id == "remote:kept"
    assert migrated[0].created_at == now
    assert migrated[0].updated_at == now
    assert snapshot.generated_count == 1
    assert snapshot.downloaded_count == 1
    assert snapshot.scenes[0].remote_result_id == "remote:kept"
    assert snapshot.scenes[0].output_path == str(output.resolve())
