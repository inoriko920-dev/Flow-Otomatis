"""Local Results / Handoff service for STEP 11 W11-04."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.application.file_integrity import is_available_output
from flow_otomatis.application.ports.download_results import DownloadResultRepositoryPort
from flow_otomatis.application.ports.episode_package import EpisodeImageVerifierPort
from flow_otomatis.application.ports.generation_jobs import GenerationJobRepositoryPort
from flow_otomatis.application.ports.result_manifest import ResultManifestWriterPort
from flow_otomatis.application.ports.workspace_repository import WorkspaceRepositoryPort
from flow_otomatis.application.services.scene_source_integrity import (
    matches_current_generated_scene,
)
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.job import GenerationJob, GenerationJobState
from flow_otomatis.domain.result import (
    DownloadRecord,
    DownloadState,
    ProjectResults,
    SceneResult,
)
from flow_otomatis.domain.scene import WorkspaceScene


class LocalResultsService:
    """Compose local Generate/Download facts and export a safe handoff manifest."""

    def __init__(
        self,
        workspace_repository: WorkspaceRepositoryPort,
        job_repository: GenerationJobRepositoryPort,
        download_repository: DownloadResultRepositoryPort,
        manifest_writer: ResultManifestWriterPort,
        *,
        image_verifier: EpisodeImageVerifierPort | None = None,
    ) -> None:
        self._workspace_repository = workspace_repository
        self._job_repository = job_repository
        self._download_repository = download_repository
        self._manifest_writer = manifest_writer
        self._image_verifier = image_verifier

    def snapshot(self, episode_id: str) -> ProjectResults:
        """Build a local result snapshot without inventing missing outcomes."""

        workspace = self._workspace_repository.load(episode_id)
        if workspace is None:
            raise InternalInvariantError(f"Workspace not found: {episode_id}")

        jobs = {job.scene_id: job for job in self._job_repository.list_for_episode(episode_id)}
        downloads = {
            record.scene_id: record
            for record in self._download_repository.list_for_episode(episode_id)
        }

        scenes: list[SceneResult] = []
        for scene in workspace.scenes:
            job = jobs.get(scene.scene_id)
            download = downloads.get(scene.scene_id)
            # A readable old MP4 alone does not attest to a current
            # GENERATED job. Reconciliation is read-only: retain historical
            # download rows and bytes, but show UNAVAILABLE until a coherent
            # Generate result can be verified again.
            verified_generate = (
                job is not None
                and job.state is GenerationJobState.GENERATED
                and bool((job.remote_result_id or "").strip())
                and self._matches_current_scene(job, scene, workspace.source_package_path)
            )
            scenes.append(
                SceneResult(
                    scene_id=scene.scene_id,
                    target_duration_s=scene.target_duration_s,
                    selected_flow_duration_s=scene.selected_flow_duration_s,
                    trim_target_s=scene.trim_target_s,
                    generate_state=job.state if job is not None else None,
                    remote_result_id=job.remote_result_id if job is not None else None,
                    download_state=(
                        (
                            DownloadState.UNAVAILABLE
                            if download.state == DownloadState.DOWNLOADED
                            and (
                                not verified_generate
                                or download.generation_remote_result_id
                                != (
                                    (job.remote_result_id if job is not None else None) or ""
                                ).strip()
                                or not self._download_repository.matches_current_generated_download(
                                    download, expected_generation=job
                                )
                                or not is_available_output(download.output_path)
                            )
                            else download.state
                        )
                        if download is not None
                        else DownloadState.NOT_DOWNLOADED
                    ),
                    output_path=download.output_path if download is not None else None,
                    take=download.take if download is not None else 1,
                    download_generation_result_id=(
                        download.generation_remote_result_id if download is not None else None
                    ),
                    updated_at=(
                        download.updated_at
                        if download is not None
                        else (job.updated_at if job is not None else None)
                    ),
                )
            )

        return ProjectResults(
            episode_id=workspace.episode_id,
            project_name=workspace.project_name,
            model=workspace.model,
            resolution=workspace.resolution,
            aspect_ratio=workspace.aspect_ratio,
            scenes=tuple(scenes),
        )

    def _matches_current_scene(
        self, job: GenerationJob, scene: WorkspaceScene, source_package_path: str
    ) -> bool:
        """Require current Scene metadata and optional canonical image evidence."""

        return matches_current_generated_scene(
            job, scene, source_package_path, self._image_verifier
        )

    def record_downloaded(
        self,
        episode_id: str,
        scene_id: str,
        output_path: str,
        *,
        take: int = 1,
    ) -> DownloadRecord:
        """Record a real/local file outcome after Generate has completed."""

        jobs = {job.scene_id: job for job in self._job_repository.list_for_episode(episode_id)}
        job = jobs.get(scene_id)
        if (
            job is None
            or job.state is not GenerationJobState.GENERATED
            or not (job.remote_result_id or "").strip()
        ):
            raise InternalInvariantError(
                "Download requires a current GENERATED job with a stable remote result ID"
            )
        workspace = self._workspace_repository.load(episode_id)
        scene = (
            next(
                (candidate for candidate in workspace.scenes if candidate.scene_id == scene_id),
                None,
            )
            if workspace is not None
            else None
        )
        if (
            workspace is None
            or scene is None
            or not self._matches_current_scene(job, scene, workspace.source_package_path)
        ):
            raise InternalInvariantError(
                "Download belongs to a previous Scene revision; refresh Generate history first"
            )
        # Inspect the original path BEFORE resolving it. Resolving first
        # would silently follow a symlink and falsely attest to an MP4 that
        # was never downloaded at the chosen output location.
        original = Path(output_path).expanduser()
        if (
            not original.is_absolute()
            or original.suffix.lower() != ".mp4"
            or not is_available_output(str(original))
        ):
            raise InternalInvariantError(
                "Download output must be an absolute, readable, nonempty regular MP4 file"
            )
        try:
            local_output = original.resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as exc:
            raise InternalInvariantError("Download output path cannot be verified") from exc
        record = DownloadRecord(
            episode_id=episode_id,
            scene_id=scene_id,
            state=DownloadState.DOWNLOADED,
            updated_at=datetime.now(UTC),
            output_path=str(local_output),
            take=max(take, 1),
            generation_remote_result_id=(job.remote_result_id or "").strip(),
        )
        if not self._download_repository.save_if_current_generate(
            record, (job.remote_result_id or "").strip()
        ):
            raise InternalInvariantError(
                "Generate result changed during atomic Download save; "
                "local video needs reconciliation."
            )
        return record

    def record_download_failed(
        self,
        episode_id: str,
        scene_id: str,
        error_message: str,
    ) -> DownloadRecord:
        """Record a Download failure without modifying Generate state.

        Caller error text is untrusted: it can include signed URLs, API keys,
        browser cookies and local paths. Do not persist it to project history.
        """

        del error_message
        record = DownloadRecord(
            episode_id=episode_id,
            scene_id=scene_id,
            state=DownloadState.FAILED,
            updated_at=datetime.now(UTC),
            error_message="Local Download failed; no confirmed MP4 was recorded.",
        )
        # An out-of-order failure must not erase a confirmed local video.
        # Use the repository's atomic conditional write, not a read-then-save.
        self._download_repository.save_failure_if_unconfirmed(record)
        return self._download_repository.get(episode_id, scene_id) or record

    def export_manifest(self, episode_id: str) -> Path:
        """Write the current credential-free local result snapshot."""

        return self._manifest_writer.write(
            self.snapshot(episode_id), recheck=lambda: self.snapshot(episode_id)
        )
