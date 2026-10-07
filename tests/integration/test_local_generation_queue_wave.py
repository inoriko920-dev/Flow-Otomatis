from __future__ import annotations

import sqlite3
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from flow_otomatis.application.ports import (
    GenerationProviderResult,
    GenerationRequest,
    GenerationSubmissionAmbiguousError,
)
from flow_otomatis.application.services import LocalGenerationQueueService
from flow_otomatis.domain.errors import StorageError
from flow_otomatis.domain.job import (
    GenerationAttentionCode,
    GenerationJobState,
)
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.persistence import (
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)


class FakeGenerationProvider:
    """Deterministic fake used only for local queue evidence."""

    def __init__(self) -> None:
        self.calls: list[GenerationRequest] = []

    def generate(self, request: GenerationRequest) -> GenerationProviderResult:
        self.calls.append(request)
        return GenerationProviderResult(remote_result_id=f"fake:{request.scene_id}")


def _scene(scene_id: str, target: float, flow: int) -> WorkspaceScene:
    return WorkspaceScene(
        scene_id=scene_id,
        image_file=f"{scene_id}.png",
        image_exists=True,
        motion_prompt=f"Prompt for {scene_id}",
        target_duration_s=target,
        recommended_flow_duration_s=flow,
        selected_flow_duration_s=flow,
        readiness=SceneReadiness.READY,
        trim_target_s=target,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
    )


def _workspace() -> WorkspaceState:
    now = datetime.now(UTC)
    return WorkspaceState(
        schema_version="1.0",
        episode_id="EP300_QUEUE",
        project_name="Queue Test",
        source_package_path=str(Path("package.zip")),
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(
            _scene("SCENE_001", 3.8, 4),
            _scene("SCENE_002", 7.3, 8),
        ),
    )


def _setup(tmp_path: Path):
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace_repo.save(_workspace())
    job_repo = SqliteGenerationJobRepository(projects_root)
    provider = FakeGenerationProvider()
    service = LocalGenerationQueueService(
        workspace_repo,
        job_repo,
        provider,
        owner_id="worker-main",
        lease_seconds=60,
    )
    return projects_root, workspace_repo, job_repo, provider, service


def test_serial_queue_is_durable_and_fake_provider_runs_in_scene_order(tmp_path: Path) -> None:
    projects_root, _workspace_repo, job_repo, provider, service = _setup(tmp_path)

    queued = service.prepare_queue("EP300_QUEUE")
    assert [job.state for job in queued] == [
        GenerationJobState.QUEUED,
        GenerationJobState.QUEUED,
    ]
    assert all(job.request_fingerprint for job in queued)

    first_claim = job_repo.claim_next(
        "EP300_QUEUE",
        "direct-owner",
        lease_seconds=60,
    )
    assert first_claim is not None
    assert first_claim.scene_id == "SCENE_001"
    assert first_claim.state is GenerationJobState.RUNNING
    assert first_claim.owner_id == "direct-owner"

    competing_repo = SqliteGenerationJobRepository(projects_root)
    assert (
        competing_repo.claim_next(
            "EP300_QUEUE",
            "other-owner",
            lease_seconds=60,
        )
        is None
    )

    job_repo.mark_generated(first_claim.job_id, "fake:SCENE_001", "direct-owner")
    remaining = service.run_until_idle("EP300_QUEUE")

    assert [request.scene_id for request in provider.calls] == ["SCENE_002"]
    assert [job.state for job in remaining] == [
        GenerationJobState.GENERATED,
        GenerationJobState.GENERATED,
    ]
    assert remaining[0].remote_result_id == "fake:SCENE_001"
    assert remaining[1].remote_result_id == "fake:SCENE_002"

    reloaded = SqliteGenerationJobRepository(projects_root).list_for_episode("EP300_QUEUE")
    assert reloaded == remaining


def test_prepare_queue_is_idempotent(tmp_path: Path) -> None:
    _root, _workspace_repo, _job_repo, _provider, service = _setup(tmp_path)

    service.prepare_queue("EP300_QUEUE")
    first = service.list_jobs("EP300_QUEUE")
    service.prepare_queue("EP300_QUEUE")
    second = service.list_jobs("EP300_QUEUE")

    assert len(second) == 2
    assert [job.request_fingerprint for job in second] == [
        job.request_fingerprint for job in first
    ]


class AmbiguousGenerationProvider:
    """Fixture that simulates a timeout after a possibly accepted submit."""

    def __init__(self) -> None:
        self.calls: list[GenerationRequest] = []

    def generate(self, request: GenerationRequest) -> GenerationProviderResult:
        self.calls.append(request)
        raise GenerationSubmissionAmbiguousError(
            "Timeout after submit; provider acceptance cannot be proven."
        )


def test_ambiguous_submit_blocks_queue_and_prevents_automatic_resubmit(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace_repo.save(_workspace())
    job_repo = SqliteGenerationJobRepository(projects_root)
    provider = AmbiguousGenerationProvider()
    service = LocalGenerationQueueService(
        workspace_repo,
        job_repo,
        provider,
        owner_id="ambiguous-worker",
    )

    service.prepare_queue("EP300_QUEUE")
    jobs = service.run_until_idle("EP300_QUEUE")

    assert [request.scene_id for request in provider.calls] == ["SCENE_001"]
    assert [job.state for job in jobs] == [
        GenerationJobState.ATTENTION_REQUIRED,
        GenerationJobState.QUEUED,
    ]
    assert jobs[0].attention_code is GenerationAttentionCode.SUBMIT_AMBIGUOUS
    assert jobs[0].submit_started_at is not None
    assert "Timeout after submit" in (jobs[0].error_message or "")

    service.prepare_queue("EP300_QUEUE")
    still_blocked = service.list_jobs("EP300_QUEUE")
    assert still_blocked[0].state is GenerationJobState.ATTENTION_REQUIRED
    assert still_blocked[0].attention_code is GenerationAttentionCode.SUBMIT_AMBIGUOUS
    assert job_repo.claim_next("EP300_QUEUE", "new-worker", lease_seconds=60) is None


def test_edit_after_enqueue_blocks_provider_until_explicit_reprepare(tmp_path: Path) -> None:
    _root, workspace_repo, _job_repo, provider, service = _setup(tmp_path)
    service.prepare_queue("EP300_QUEUE")

    workspace = workspace_repo.load("EP300_QUEUE")
    assert workspace is not None
    changed_first = replace(
        workspace.scenes[0],
        motion_prompt="Changed after enqueue.",
    )
    workspace_repo.update(
        replace(workspace, scenes=(changed_first, workspace.scenes[1]))
    )

    blocked = service.run_next("EP300_QUEUE")
    assert blocked is not None
    assert blocked.state is GenerationJobState.ATTENTION_REQUIRED
    assert blocked.attention_code is GenerationAttentionCode.REQUEST_STALE
    assert provider.calls == []

    reprepared = service.prepare_queue("EP300_QUEUE")
    assert reprepared[0].state is GenerationJobState.QUEUED
    assert reprepared[0].attention_code is None

    generated = service.run_next("EP300_QUEUE")
    assert generated is not None
    assert generated.state is GenerationJobState.GENERATED
    assert [request.motion_prompt for request in provider.calls] == ["Changed after enqueue."]


def test_image_missing_after_enqueue_blocks_provider_without_mixing_revision(
    tmp_path: Path,
) -> None:
    _root, workspace_repo, _job_repo, provider, service = _setup(tmp_path)
    service.prepare_queue("EP300_QUEUE")

    workspace = workspace_repo.load("EP300_QUEUE")
    assert workspace is not None
    missing_first = replace(
        workspace.scenes[0],
        image_exists=False,
        readiness=SceneReadiness.MISSING_IMAGE,
    )
    workspace_repo.update(
        replace(workspace, scenes=(missing_first, workspace.scenes[1]))
    )

    blocked = service.run_next("EP300_QUEUE")

    assert blocked is not None
    assert blocked.state is GenerationJobState.ATTENTION_REQUIRED
    assert blocked.attention_code is GenerationAttentionCode.REQUEST_STALE
    assert provider.calls == []


def test_active_owner_lease_cannot_be_stolen_by_second_instance(tmp_path: Path) -> None:
    projects_root, _workspace_repo, job_repo, _provider, service = _setup(tmp_path)
    service.prepare_queue("EP300_QUEUE")
    t0 = datetime(2026, 10, 7, 15, 0, tzinfo=UTC)

    first = job_repo.claim_next(
        "EP300_QUEUE",
        "owner-a",
        lease_seconds=120,
        now=t0,
    )
    assert first is not None

    other = SqliteGenerationJobRepository(projects_root)
    second = other.claim_next(
        "EP300_QUEUE",
        "owner-b",
        lease_seconds=120,
        now=t0 + timedelta(seconds=30),
    )

    assert second is None
    persisted = job_repo.list_for_episode("EP300_QUEUE")[0]
    assert persisted.state is GenerationJobState.RUNNING
    assert persisted.owner_id == "owner-a"


def test_expired_orphan_before_and_after_submit_boundary_are_distinguished(
    tmp_path: Path,
) -> None:
    _root, _workspace_repo, job_repo, provider, service = _setup(tmp_path)
    service.prepare_queue("EP300_QUEUE")
    t0 = datetime(2026, 10, 7, 15, 0, tzinfo=UTC)

    pre_submit = job_repo.claim_next(
        "EP300_QUEUE",
        "owner-pre",
        lease_seconds=1,
        now=t0,
    )
    assert pre_submit is not None

    recovered = job_repo.recover_expired(
        "EP300_QUEUE",
        now=t0 + timedelta(seconds=2),
    )
    assert len(recovered) == 1
    assert recovered[0].attention_code is GenerationAttentionCode.ORPHAN_PRE_SUBMIT
    assert recovered[0].submit_started_at is None
    assert provider.calls == []

    service.prepare_queue("EP300_QUEUE")
    t1 = t0 + timedelta(minutes=1)
    post_submit = job_repo.claim_next(
        "EP300_QUEUE",
        "owner-post",
        lease_seconds=1,
        now=t1,
    )
    assert post_submit is not None
    job_repo.mark_submit_started(
        post_submit.job_id,
        "owner-post",
        lease_seconds=1,
        now=t1,
    )

    recovered_again = job_repo.recover_expired(
        "EP300_QUEUE",
        now=t1 + timedelta(seconds=2),
    )
    assert len(recovered_again) == 1
    assert recovered_again[0].attention_code is GenerationAttentionCode.ORPHAN_POSSIBLE_SUBMIT
    assert recovered_again[0].submit_started_at == t1
    assert provider.calls == []

    service.prepare_queue("EP300_QUEUE")
    still_blocked = service.list_jobs("EP300_QUEUE")[0]
    assert still_blocked.attention_code is GenerationAttentionCode.ORPHAN_POSSIBLE_SUBMIT


def _create_legacy_job_table(db_path: Path, *, state: str = "QUEUED") -> None:
    now = datetime(2026, 10, 7, 15, 0, tzinfo=UTC).isoformat()
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)
            """,
            (
                "EP300_QUEUE:SCENE_001:GENERATE",
                "EP300_QUEUE",
                "SCENE_001",
                3.8,
                4,
                state,
                now,
                now,
            ),
        )
        connection.commit()


def test_legacy_unverified_queue_is_parked_until_explicit_reprepare(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace_repo.save(_workspace())
    db_path = projects_root / "EP300_QUEUE" / "project.sqlite3"
    _create_legacy_job_table(db_path)

    job_repo = SqliteGenerationJobRepository(projects_root)
    migrated = job_repo.list_for_episode("EP300_QUEUE")

    assert migrated[0].state is GenerationJobState.ATTENTION_REQUIRED
    assert migrated[0].attention_code is GenerationAttentionCode.LEGACY_UNVERIFIED
    assert job_repo.claim_next("EP300_QUEUE", "owner", lease_seconds=60) is None

    provider = FakeGenerationProvider()
    service = LocalGenerationQueueService(
        workspace_repo,
        job_repo,
        provider,
        owner_id="new-worker",
    )
    reprepared = service.prepare_queue("EP300_QUEUE")
    assert reprepared[0].state is GenerationJobState.QUEUED
    assert reprepared[0].request_fingerprint is not None


def test_failed_schema_migration_rolls_back_all_added_columns(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace_repo.save(_workspace())
    db_path = projects_root / "EP300_QUEUE" / "project.sqlite3"
    _create_legacy_job_table(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TRIGGER block_generation_job_migration
            BEFORE UPDATE ON generation_jobs
            BEGIN
                SELECT RAISE(ABORT, 'migration blocked');
            END
            """
        )
        connection.commit()

    job_repo = SqliteGenerationJobRepository(projects_root)
    with pytest.raises(StorageError):
        job_repo.list_for_episode("EP300_QUEUE")

    with sqlite3.connect(db_path) as connection:
        columns = {
            str(row[1])
            for row in connection.execute("PRAGMA table_info(generation_jobs)").fetchall()
        }
        meta = connection.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'generation_job_schema'
            """
        ).fetchone()

    assert "request_fingerprint" not in columns
    assert "owner_id" not in columns
    assert meta is None
