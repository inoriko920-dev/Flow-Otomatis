"""Durable serial R1 queue engine for STEP 11 W11-03."""

from __future__ import annotations

from datetime import UTC, datetime

from flow_otomatis.application.ports.generation_jobs import GenerationJobRepositoryPort
from flow_otomatis.application.ports.generation_provider import (
    GenerationProviderPort,
    GenerationRequest,
)
from flow_otomatis.application.ports.workspace_repository import WorkspaceRepositoryPort
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene


class LocalGenerationQueueService:
    """Prepare and execute generation jobs one at a time."""

    def __init__(
        self,
        workspace_repository: WorkspaceRepositoryPort,
        job_repository: GenerationJobRepositoryPort,
        provider: GenerationProviderPort,
    ) -> None:
        self._workspace_repository = workspace_repository
        self._job_repository = job_repository
        self._provider = provider

    def prepare_queue(self, episode_id: str) -> tuple[GenerationJob, ...]:
        """Idempotently enqueue every locally READY Scene."""

        workspace = self._workspace_repository.load(episode_id)
        if workspace is None:
            raise InternalInvariantError(f"Workspace not found: {episode_id}")

        now = datetime.now(UTC)
        jobs: list[GenerationJob] = []
        for scene in workspace.scenes:
            if scene.readiness is not SceneReadiness.READY:
                continue
            if scene.selected_flow_duration_s is None:
                continue
            jobs.append(
                GenerationJob(
                    job_id=f"{episode_id}:{scene.scene_id}:GENERATE",
                    episode_id=episode_id,
                    scene_id=scene.scene_id,
                    target_duration_s=scene.target_duration_s,
                    flow_duration_s=scene.selected_flow_duration_s,
                    state=GenerationJobState.QUEUED,
                    created_at=now,
                    updated_at=now,
                )
            )
        self._job_repository.ensure_jobs(jobs)
        return self._job_repository.list_for_episode(episode_id)

    def run_next(self, episode_id: str) -> GenerationJob | None:
        """Claim and execute at most one generation job."""

        job = self._job_repository.claim_next(episode_id)
        if job is None:
            return None

        workspace = self._workspace_repository.load(episode_id)
        if workspace is None:
            return self._job_repository.mark_failed(job.job_id, "Workspace disappeared")

        try:
            scene = self._scene(workspace.scenes, job.scene_id)
            request = GenerationRequest(
                episode_id=episode_id,
                scene_id=scene.scene_id,
                image_file=scene.image_file,
                motion_prompt=scene.motion_prompt,
                target_duration_s=job.target_duration_s,
                flow_duration_s=job.flow_duration_s,
                model=scene.model,
                resolution=scene.resolution,
                aspect_ratio=scene.aspect_ratio,
            )
            result = self._provider.generate(request)
        except Exception as exc:
            return self._job_repository.mark_failed(job.job_id, str(exc)[:500])

        return self._job_repository.mark_generated(job.job_id, result.remote_result_id)

    def run_until_idle(self, episode_id: str) -> tuple[GenerationJob, ...]:
        """Execute the local queue serially until no QUEUED job can be claimed."""

        while self.run_next(episode_id) is not None:
            pass
        return self._job_repository.list_for_episode(episode_id)

    def list_jobs(self, episode_id: str) -> tuple[GenerationJob, ...]:
        """Return persisted local queue state."""

        return self._job_repository.list_for_episode(episode_id)

    def _scene(
        self,
        scenes: tuple[WorkspaceScene, ...],
        scene_id: str,
    ) -> WorkspaceScene:
        for scene in scenes:
            if scene.scene_id == scene_id:
                return scene
        raise InternalInvariantError(f"Queued Scene no longer exists: {scene_id}")
