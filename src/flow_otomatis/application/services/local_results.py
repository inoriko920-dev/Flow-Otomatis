"""Local Results / Handoff service for STEP 11 W11-04."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.application.ports.download_results import DownloadResultRepositoryPort
from flow_otomatis.application.ports.generation_jobs import GenerationJobRepositoryPort
from flow_otomatis.application.ports.result_manifest import ResultManifestWriterPort
from flow_otomatis.application.ports.workspace_repository import WorkspaceRepositoryPort
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.job import GenerationJobState
from flow_otomatis.domain.result import (
    DownloadRecord,
    DownloadState,
    ProjectResults,
    SceneResult,
)


class LocalResultsService:
    """Compose local Generate/Download facts and export a safe handoff manifest."""

    def __init__(
        self,
        workspace_repository: WorkspaceRepositoryPort,
        job_repository: GenerationJobRepositoryPort,
        download_repository: DownloadResultRepositoryPort,
        manifest_writer: ResultManifestWriterPort,
    ) -> None:
        self._workspace_repository = workspace_repository
        self._job_repository = job_repository
        self._download_repository = download_repository
        self._manifest_writer = manifest_writer

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
            scenes.append(
                SceneResult(
                    scene_id=scene.scene_id,
                    target_duration_s=scene.target_duration_s,
                    selected_flow_duration_s=scene.selected_flow_duration_s,
                    trim_target_s=scene.trim_target_s,
                    generate_state=job.state if job is not None else None,
                    remote_result_id=job.remote_result_id if job is not None else None,
                    download_state=(
                        download.state if download is not None else DownloadState.NOT_DOWNLOADED
                    ),
                    output_path=download.output_path if download is not None else None,
                    take=download.take if download is not None else 1,
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
        if job is None or job.state is not GenerationJobState.GENERATED:
            raise InternalInvariantError(
                "Download cannot be marked successful before Generate is GENERATED"
            )
        local_output = Path(output_path).expanduser().resolve()
        if not local_output.is_file():
            raise InternalInvariantError("Download output file does not exist locally")
        record = DownloadRecord(
            episode_id=episode_id,
            scene_id=scene_id,
            state=DownloadState.DOWNLOADED,
            updated_at=datetime.now(UTC),
            output_path=str(local_output),
            take=max(take, 1),
        )
        self._download_repository.save(record)
        return record

    def record_download_failed(
        self,
        episode_id: str,
        scene_id: str,
        error_message: str,
    ) -> DownloadRecord:
        """Record a Download failure without modifying Generate state."""

        record = DownloadRecord(
            episode_id=episode_id,
            scene_id=scene_id,
            state=DownloadState.FAILED,
            updated_at=datetime.now(UTC),
            error_message=error_message[:500],
        )
        self._download_repository.save(record)
        return record

    def export_manifest(self, episode_id: str) -> Path:
        """Write the current credential-free local result snapshot."""

        return self._manifest_writer.write(self.snapshot(episode_id))
