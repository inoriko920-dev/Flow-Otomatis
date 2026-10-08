"""Durable serial generation queue with coherent request revisions and worker leases."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from flow_otomatis.application.ports.episode_package import EpisodeImageVerifierPort
from flow_otomatis.application.ports.generation_jobs import GenerationJobRepositoryPort
from flow_otomatis.application.ports.generation_provider import (
    GenerationAuthenticationRequiredError,
    GenerationCancelledError,
    GenerationProviderPort,
    GenerationRequest,
    GenerationSubmissionAmbiguousError,
)
from flow_otomatis.application.ports.workspace_repository import WorkspaceRepositoryPort
from flow_otomatis.domain.errors import (
    InternalInvariantError,
    PackageSecurityError,
    PackageValidationError,
)
from flow_otomatis.domain.job import (
    GenerationAttentionCode,
    GenerationJob,
    GenerationJobState,
)
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene

_DEFAULT_LEASE_SECONDS = 30 * 60


def _scene_fingerprint(episode_id: str, scene: WorkspaceScene, image_digest: str) -> str:
    payload = {
        "episode_id": episode_id,
        "scene_id": scene.scene_id,
        "image_file": scene.image_file,
        "image_exists": scene.image_exists,
        "image_sha256": image_digest,
        "motion_prompt": scene.motion_prompt,
        "target_duration_s": scene.target_duration_s,
        "flow_duration_s": scene.selected_flow_duration_s,
        "model": scene.model,
        "resolution": scene.resolution,
        "aspect_ratio": scene.aspect_ratio,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class LocalGenerationQueueService:
    """Prepare and execute generation jobs one coherent revision at a time."""

    def __init__(
        self,
        workspace_repository: WorkspaceRepositoryPort,
        job_repository: GenerationJobRepositoryPort,
        provider: GenerationProviderPort,
        *,
        image_verifier: EpisodeImageVerifierPort | None = None,
        owner_id: str | None = None,
        lease_seconds: int = _DEFAULT_LEASE_SECONDS,
    ) -> None:
        self._workspace_repository = workspace_repository
        self._job_repository = job_repository
        self._provider = provider
        self._image_verifier = image_verifier
        self._owner_id = owner_id or uuid4().hex
        self._lease_seconds = max(lease_seconds, 1)

    @property
    def owner_id(self) -> str:
        """Return the process-local durable owner identity used for claims."""

        return self._owner_id

    def prepare_queue(self, episode_id: str) -> tuple[GenerationJob, ...]:
        """Explicitly prepare every locally READY Scene as one coherent request revision."""

        self._job_repository.recover_expired(episode_id)
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
                    image_file=scene.image_file,
                    motion_prompt=scene.motion_prompt,
                    model=scene.model,
                    resolution=scene.resolution,
                    aspect_ratio=scene.aspect_ratio,
                    request_fingerprint=_scene_fingerprint(
                        episode_id,
                        scene,
                        self._image_digest(workspace.source_package_path, scene),
                    ),
                )
            )
        self._job_repository.prepare_jobs(jobs)
        return self._job_repository.list_for_episode(episode_id)

    def run_next(self, episode_id: str) -> GenerationJob | None:
        """Claim and execute at most one verified generation job."""

        self._job_repository.recover_expired(episode_id)
        job = self._job_repository.claim_next(
            episode_id,
            self._owner_id,
            lease_seconds=self._lease_seconds,
        )
        if job is None:
            return None

        workspace = self._workspace_repository.load(episode_id)
        if workspace is None:
            return self._job_repository.mark_failed(
                job.job_id,
                "Workspace disappeared",
                self._owner_id,
            )

        try:
            scene = self._scene(workspace.scenes, job.scene_id)
        except InternalInvariantError as exc:
            return self._job_repository.mark_attention(
                job.job_id,
                str(exc)[:500],
                GenerationAttentionCode.REQUEST_STALE,
                self._owner_id,
            )

        stale_reason = self._stale_reason(episode_id, workspace.source_package_path, scene, job)
        if stale_reason is not None:
            return self._job_repository.mark_attention(
                job.job_id,
                stale_reason,
                GenerationAttentionCode.REQUEST_STALE,
                self._owner_id,
            )

        request = GenerationRequest(
            episode_id=job.episode_id,
            scene_id=job.scene_id,
            image_file=job.image_file or "",
            motion_prompt=job.motion_prompt or "",
            target_duration_s=job.target_duration_s,
            flow_duration_s=job.flow_duration_s,
            model=job.model or "",
            resolution=job.resolution or "",
            aspect_ratio=job.aspect_ratio or "",
        )

        self._job_repository.mark_submit_started(
            job.job_id,
            self._owner_id,
            lease_seconds=self._lease_seconds,
        )
        try:
            result = self._provider.generate(request)
        except GenerationSubmissionAmbiguousError as exc:
            return self._job_repository.mark_attention(
                job.job_id,
                str(exc)[:500],
                GenerationAttentionCode.SUBMIT_AMBIGUOUS,
                self._owner_id,
            )
        except GenerationAuthenticationRequiredError as exc:
            return self._job_repository.mark_attention(
                job.job_id,
                str(exc)[:500],
                GenerationAttentionCode.AUTH_REQUIRED,
                self._owner_id,
            )
        except GenerationCancelledError as exc:
            return self._job_repository.mark_failed(
                job.job_id,
                f"Cancelled: {str(exc)[:480]}",
                self._owner_id,
            )
        except Exception as exc:
            return self._job_repository.mark_attention(
                job.job_id,
                f"Provider outcome uncertain after submit boundary: {str(exc)[:430]}",
                GenerationAttentionCode.SUBMIT_AMBIGUOUS,
                self._owner_id,
            )

        return self._job_repository.mark_generated(
            job.job_id,
            result.remote_result_id,
            self._owner_id,
        )

    def run_until_idle(self, episode_id: str) -> tuple[GenerationJob, ...]:
        """Execute serially until no safe QUEUED job can be claimed."""

        while self.run_next(episode_id) is not None:
            pass
        return self._job_repository.list_for_episode(episode_id)

    def recover_orphans(
        self,
        episode_id: str,
        *,
        now: datetime | None = None,
    ) -> tuple[GenerationJob, ...]:
        """Classify proven expired RUNNING leases without submitting anything."""

        return self._job_repository.recover_expired(episode_id, now=now)

    def list_jobs(self, episode_id: str) -> tuple[GenerationJob, ...]:
        """Return persisted queue state after safe expired-lease classification."""

        self._job_repository.recover_expired(episode_id)
        return self._job_repository.list_for_episode(episode_id)

    def _stale_reason(
        self,
        episode_id: str,
        source_package_path: str,
        scene: WorkspaceScene,
        job: GenerationJob,
    ) -> str | None:
        if not job.has_verified_request_snapshot:
            return "Queued request has no verifiable prepared revision; prepare the Scene again."
        if scene.readiness is not SceneReadiness.READY:
            return (
                f"Scene {scene.scene_id} is no longer READY "
                f"({scene.readiness.value}); prepare the queue again after fixing inputs."
            )
        if scene.selected_flow_duration_s is None:
            return f"Scene {scene.scene_id} no longer has a selected Flow duration."
        if not scene.image_exists:
            return f"Scene {scene.scene_id} image is no longer available."
        try:
            current_digest = self._image_digest(source_package_path, scene)
        except PackageValidationError, PackageSecurityError, InternalInvariantError:
            return (
                f"Scene {scene.scene_id}: gambar hilang atau tidak bisa diverifikasi. "
                "Persiapkan antrean kembali sebelum Generate."
            )
        if job.request_fingerprint != _scene_fingerprint(episode_id, scene, current_digest):
            return (
                f"Scene {scene.scene_id} or image bytes changed after prepare; "
                "prepare the queue again before Generate."
            )
        if (
            job.image_file != scene.image_file
            or job.motion_prompt != scene.motion_prompt
            or job.target_duration_s != scene.target_duration_s
            or job.flow_duration_s != scene.selected_flow_duration_s
            or job.model != scene.model
            or job.resolution != scene.resolution
            or job.aspect_ratio != scene.aspect_ratio
        ):
            return (
                f"Scene {scene.scene_id} request snapshot does not match current planning; "
                "prepare the queue again."
            )
        return None

    def _image_digest(self, source_package_path: str, scene: WorkspaceScene) -> str:
        """Fail closed when a canonical content verifier was not composed."""

        if self._image_verifier is None:
            raise InternalInvariantError("Generation input verifier is not configured")
        return self._image_verifier.image_digest(
            Path(source_package_path), scene.scene_id, scene.image_file
        )

    def _scene(
        self,
        scenes: tuple[WorkspaceScene, ...],
        scene_id: str,
    ) -> WorkspaceScene:
        for scene in scenes:
            if scene.scene_id == scene_id:
                return scene
        raise InternalInvariantError(f"Queued Scene no longer exists: {scene_id}")
