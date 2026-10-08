from __future__ import annotations

import json
import sqlite3
import zipfile
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
from flow_otomatis.domain.errors import PackageValidationError, StorageError
from flow_otomatis.domain.job import (
    GenerationAttentionCode,
    GenerationJobState,
)
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.filesystem import EpisodePackageReader
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


def _workspace_with_source(tmp_path: Path, *, zip_source: bool = False) -> WorkspaceState:
    """Create real import-compatible folder or ZIP image evidence for queue tests."""

    workspace = _workspace()
    manifest = {
        "schema_version": "1.0",
        "episode_id": workspace.episode_id,
        "project_name": workspace.project_name,
        "production_profile": {
            "model": workspace.model,
            "resolution": workspace.resolution,
            "aspect_ratio": workspace.aspect_ratio,
        },
        "scene_count": len(workspace.scenes),
        "scenes": [
            {
                "scene_id": scene.scene_id,
                "image_file": scene.image_file,
                "motion_prompt": scene.motion_prompt,
                "target_duration_s": scene.target_duration_s,
                "recommended_flow_duration_s": scene.recommended_flow_duration_s,
                "selected_flow_duration_s": scene.selected_flow_duration_s,
                "trim_target_s": scene.trim_target_s,
                "model": scene.model,
                "resolution": scene.resolution,
                "aspect_ratio": scene.aspect_ratio,
                "status": "READY",
            }
            for scene in workspace.scenes
        ],
        "created_at": workspace.created_at.isoformat(),
        "source_versions": {},
    }
    if zip_source:
        package_zip = tmp_path / "source.zip"
        with zipfile.ZipFile(package_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("FLOW_OTOMATIS_IMPORT.json", json.dumps(manifest))
            for scene in workspace.scenes:
                archive.writestr(scene.image_file, f"image-bytes-{scene.scene_id}".encode())
        return replace(workspace, source_package_path=str(package_zip))

    package_root = tmp_path / "package"
    package_root.mkdir(parents=True, exist_ok=True)
    manifest_path = package_root / "FLOW_OTOMATIS_IMPORT.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    for scene in workspace.scenes:
        (package_root / scene.image_file).write_bytes(
            f"image-bytes-{scene.scene_id}".encode()
        )
    return replace(workspace, source_package_path=str(manifest_path))


def _setup(tmp_path: Path):
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace_repo.save(_workspace_with_source(tmp_path))
    job_repo = SqliteGenerationJobRepository(projects_root)
    provider = FakeGenerationProvider()
    service = LocalGenerationQueueService(
        workspace_repo,
        job_repo,
        provider,
        image_verifier=EpisodePackageReader(),
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
    assert [job.request_fingerprint for job in second] == [job.request_fingerprint for job in first]


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
    workspace_repo.save(_workspace_with_source(tmp_path))
    job_repo = SqliteGenerationJobRepository(projects_root)
    provider = AmbiguousGenerationProvider()
    service = LocalGenerationQueueService(
        workspace_repo,
        job_repo,
        provider,
        image_verifier=EpisodePackageReader(),
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
    workspace_repo.update(replace(workspace, scenes=(changed_first, workspace.scenes[1])))

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
    workspace_repo.update(replace(workspace, scenes=(missing_first, workspace.scenes[1])))

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
    workspace_repo.save(_workspace_with_source(tmp_path))
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
        image_verifier=EpisodePackageReader(),
        owner_id="new-worker",
    )
    reprepared = service.prepare_queue("EP300_QUEUE")
    assert reprepared[0].state is GenerationJobState.QUEUED
    assert reprepared[0].request_fingerprint is not None


def test_failed_schema_migration_rolls_back_all_added_columns(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace_repo.save(_workspace_with_source(tmp_path))
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

def test_t09_folder_image_deleted_after_prepare_blocks_submit(tmp_path: Path) -> None:
    _root, workspace_repo, _jobs, provider, service = _setup(tmp_path)
    service.prepare_queue("EP300_QUEUE")
    workspace = workspace_repo.load("EP300_QUEUE")
    assert workspace is not None
    image = Path(workspace.source_package_path).parent / workspace.scenes[0].image_file
    image.unlink()

    outcome = service.run_next("EP300_QUEUE")
    assert outcome is not None
    assert outcome.state is GenerationJobState.ATTENTION_REQUIRED
    assert outcome.attention_code is GenerationAttentionCode.REQUEST_STALE
    assert outcome.submit_started_at is None
    assert provider.calls == []


@pytest.mark.parametrize("change", ["delete_zip", "remove_entry"])
def test_t10_zip_source_unavailable_blocks_provider(tmp_path: Path, change: str) -> None:
    projects_root = tmp_path / "projects"
    repo = SqliteWorkspaceRepository(projects_root)
    workspace = _workspace_with_source(tmp_path, zip_source=True)
    repo.save(workspace)
    jobs = SqliteGenerationJobRepository(projects_root)
    provider = FakeGenerationProvider()
    service = LocalGenerationQueueService(
        repo, jobs, provider, image_verifier=EpisodePackageReader()
    )
    service.prepare_queue(workspace.episode_id)
    zip_path = Path(workspace.source_package_path)
    if change == "delete_zip":
        zip_path.unlink()
    else:
        with zipfile.ZipFile(zip_path, "r") as archive:
            retained = {
                name: archive.read(name)
                for name in archive.namelist()
                if name != workspace.scenes[0].image_file
            }
        with zipfile.ZipFile(zip_path, "w") as archive:
            for name, data in retained.items():
                archive.writestr(name, data)

    result = service.run_next(workspace.episode_id)
    assert result is not None
    assert result.attention_code is GenerationAttentionCode.REQUEST_STALE
    assert result.submit_started_at is None
    assert provider.calls == []


def test_t11_modified_image_bytes_same_name_blocks_and_reprepare_works(tmp_path: Path) -> None:
    _root, repo, _jobs, provider, service = _setup(tmp_path)
    service.prepare_queue("EP300_QUEUE")
    workspace = repo.load("EP300_QUEUE")
    assert workspace is not None
    image = Path(workspace.source_package_path).parent / workspace.scenes[0].image_file
    image.write_bytes(b"new-content-same-file-name")

    result = service.run_next("EP300_QUEUE")
    assert result is not None
    assert result.attention_code is GenerationAttentionCode.REQUEST_STALE
    assert provider.calls == []
    service.prepare_queue("EP300_QUEUE")
    generated = service.run_next("EP300_QUEUE")
    assert generated is not None
    assert generated.state is GenerationJobState.GENERATED
    assert len(provider.calls) == 1


def test_t12_unreadable_image_maps_to_pre_submit_attention(tmp_path: Path, monkeypatch) -> None:
    _root, repo, _jobs, provider, service = _setup(tmp_path)
    service.prepare_queue("EP300_QUEUE")
    workspace = repo.load("EP300_QUEUE")
    assert workspace is not None
    image = (Path(workspace.source_package_path).parent / workspace.scenes[0].image_file)
    original_open = Path.open

    def deny_image_open(self: Path, *args, **kwargs):
        if self == image:
            raise PermissionError("synthetic access denied")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", deny_image_open)
    outcome = service.run_next("EP300_QUEUE")
    assert outcome is not None
    assert outcome.attention_code is GenerationAttentionCode.REQUEST_STALE
    assert outcome.submit_started_at is None
    assert provider.calls == []


def test_t13_verified_zip_image_submits_once_and_ambiguity_is_not_retried(
    tmp_path: Path,
) -> None:
    root = tmp_path / "projects"
    workspace = _workspace_with_source(tmp_path, zip_source=True)
    repo = SqliteWorkspaceRepository(root)
    repo.save(workspace)
    jobs = SqliteGenerationJobRepository(root)
    provider = AmbiguousGenerationProvider()
    service = LocalGenerationQueueService(
        repo, jobs, provider, image_verifier=EpisodePackageReader()
    )
    service.prepare_queue(workspace.episode_id)
    outcome = service.run_next(workspace.episode_id)
    assert outcome is not None
    assert outcome.attention_code is GenerationAttentionCode.SUBMIT_AMBIGUOUS
    assert len(provider.calls) == 1
    assert service.run_next(workspace.episode_id) is None
    assert len(provider.calls) == 1


def test_legacy_fingerprint_without_image_bytes_never_submits(tmp_path: Path) -> None:
    from flow_otomatis.application.services.local_generation_queue import _scene_fingerprint

    _root, repo, jobs, provider, service = _setup(tmp_path)
    prepared = service.prepare_queue("EP300_QUEUE")
    workspace = repo.load("EP300_QUEUE")
    assert workspace is not None
    scene = workspace.scenes[0]
    import hashlib

    legacy_payload = {
        "episode_id": workspace.episode_id,
        "scene_id": scene.scene_id,
        "image_file": scene.image_file,
        "image_exists": scene.image_exists,
        "motion_prompt": scene.motion_prompt,
        "target_duration_s": scene.target_duration_s,
        "flow_duration_s": scene.selected_flow_duration_s,
        "model": scene.model,
        "resolution": scene.resolution,
        "aspect_ratio": scene.aspect_ratio,
    }
    old_digest = hashlib.sha256(
        json.dumps(legacy_payload, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False).encode()
    ).hexdigest()
    assert old_digest != prepared[0].request_fingerprint
    assert len(_scene_fingerprint(workspace.episode_id, scene, "1" * 64)) == 64
    with sqlite3.connect(_root / workspace.episode_id / "project.sqlite3") as connection:
        connection.execute(
            "UPDATE generation_jobs SET request_fingerprint=? WHERE scene_id=?",
            (old_digest, scene.scene_id),
        )
        connection.commit()
    blocked = service.run_next(workspace.episode_id)
    assert blocked is not None
    assert blocked.attention_code is GenerationAttentionCode.REQUEST_STALE
    assert provider.calls == []


def test_prepare_requires_canonical_verifier(tmp_path: Path) -> None:
    root = tmp_path / "projects"
    repo = SqliteWorkspaceRepository(root)
    repo.save(_workspace_with_source(tmp_path))
    jobs = SqliteGenerationJobRepository(root)
    service = LocalGenerationQueueService(repo, jobs, FakeGenerationProvider())
    with pytest.raises(Exception, match="verifier"):
        service.prepare_queue("EP300_QUEUE")
    assert jobs.list_for_episode("EP300_QUEUE") == ()

