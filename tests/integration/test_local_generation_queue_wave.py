from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.application.ports import (
    GenerationProviderResult,
    GenerationRequest,
    GenerationSubmissionAmbiguousError,
)
from flow_otomatis.application.services import LocalGenerationQueueService
from flow_otomatis.domain.job import GenerationJobState
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.infrastructure.persistence import (
    SqliteGenerationJobRepository,
    SqliteWorkspaceRepository,
)


class FakeGenerationProvider:
    """Deterministic fake used only for STEP 11 local queue evidence."""

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


def test_serial_queue_is_durable_and_fake_provider_runs_in_scene_order(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace_repo.save(_workspace())
    job_repo = SqliteGenerationJobRepository(projects_root)
    provider = FakeGenerationProvider()
    service = LocalGenerationQueueService(workspace_repo, job_repo, provider)

    queued = service.prepare_queue("EP300_QUEUE")
    assert [job.state for job in queued] == [
        GenerationJobState.QUEUED,
        GenerationJobState.QUEUED,
    ]

    first_claim = job_repo.claim_next("EP300_QUEUE")
    assert first_claim is not None
    assert first_claim.scene_id == "SCENE_001"
    assert first_claim.state is GenerationJobState.RUNNING

    assert job_repo.claim_next("EP300_QUEUE") is None

    job_repo.mark_generated(first_claim.job_id, "fake:SCENE_001")
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
    projects_root = tmp_path / "projects"
    workspace_repo = SqliteWorkspaceRepository(projects_root)
    workspace_repo.save(_workspace())
    job_repo = SqliteGenerationJobRepository(projects_root)
    service = LocalGenerationQueueService(
        workspace_repo,
        job_repo,
        FakeGenerationProvider(),
    )

    service.prepare_queue("EP300_QUEUE")
    service.prepare_queue("EP300_QUEUE")

    assert len(service.list_jobs("EP300_QUEUE")) == 2


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
    service = LocalGenerationQueueService(workspace_repo, job_repo, provider)

    service.prepare_queue("EP300_QUEUE")
    jobs = service.run_until_idle("EP300_QUEUE")

    assert [request.scene_id for request in provider.calls] == ["SCENE_001"]
    assert [job.state for job in jobs] == [
        GenerationJobState.ATTENTION_REQUIRED,
        GenerationJobState.QUEUED,
    ]
    assert "Timeout after submit" in (jobs[0].error_message or "")
    assert job_repo.claim_next("EP300_QUEUE") is None
