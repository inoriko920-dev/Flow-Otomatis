"""Safe generated-media download orchestration for STEP 12 I12-03A."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.application.ports.download_results import DownloadResultRepositoryPort
from flow_otomatis.application.ports.generated_media_download import (
    GeneratedMediaDownloadProviderPort,
    GeneratedMediaDownloadRequest,
    MediaDownloadProviderError,
)
from flow_otomatis.application.ports.generation_jobs import GenerationJobRepositoryPort
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.job import GenerationJobState
from flow_otomatis.domain.result import DownloadRecord, DownloadState


class GeneratedMediaDownloadService:
    """Download confirmed Generate results into canonical per-project files."""

    def __init__(
        self,
        job_repository: GenerationJobRepositoryPort,
        download_repository: DownloadResultRepositoryPort,
        provider: GeneratedMediaDownloadProviderPort,
        projects_root: Path,
    ) -> None:
        self._job_repository = job_repository
        self._download_repository = download_repository
        self._provider = provider
        self._projects_root = projects_root

    def download_scene(
        self,
        episode_id: str,
        scene_id: str,
        *,
        take: int = 1,
    ) -> DownloadRecord:
        """Download one GENERATED Scene once and persist only a confirmed local file."""

        self._validate_segment("episode_id", episode_id)
        self._validate_segment("scene_id", scene_id)
        normalized_take = max(int(take), 1)

        existing = self._download_repository.get(episode_id, scene_id)
        if (
            existing is not None
            and existing.state == DownloadState.DOWNLOADED
            and existing.output_path is not None
        ):
            existing_path = Path(existing.output_path)
            if existing_path.is_file() and existing_path.stat().st_size > 0:
                return existing

        jobs = {job.scene_id: job for job in self._job_repository.list_for_episode(episode_id)}
        job = jobs.get(scene_id)
        if job is None:
            raise InternalInvariantError(f"Generation job not found: {episode_id}/{scene_id}")
        if job.state is not GenerationJobState.GENERATED:
            raise InternalInvariantError(
                "Download requires a confirmed GENERATED job and never starts Generate implicitly."
            )

        remote_result_id = (job.remote_result_id or "").strip()
        if not remote_result_id:
            raise InternalInvariantError(
                "Download requires a stable remote result identifier from Generate."
            )

        destination = self._destination_path(episode_id, scene_id, normalized_take)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise InternalInvariantError(
                "Download destination already exists and will not be overwritten: "
                f"{destination.name}"
            )

        request = GeneratedMediaDownloadRequest(
            episode_id=episode_id,
            scene_id=scene_id,
            remote_result_id=remote_result_id,
            destination_path=str(destination),
        )
        try:
            result = self._provider.download(request)
        except MediaDownloadProviderError as exc:
            record = DownloadRecord(
                episode_id=episode_id,
                scene_id=scene_id,
                state=DownloadState.FAILED,
                updated_at=datetime.now(UTC),
                take=normalized_take,
                error_message=str(exc)[:500],
            )
            self._download_repository.save(record)
            raise

        output = Path(result.output_path).expanduser().resolve()
        if output != destination.resolve():
            raise InternalInvariantError("Download provider returned an unexpected output path.")
        if not output.is_file() or output.stat().st_size <= 0:
            raise InternalInvariantError(
                "Download provider did not produce a non-empty local file."
            )

        record = DownloadRecord(
            episode_id=episode_id,
            scene_id=scene_id,
            state=DownloadState.DOWNLOADED,
            updated_at=datetime.now(UTC),
            output_path=str(output),
            take=normalized_take,
        )
        self._download_repository.save(record)
        return record

    def _destination_path(self, episode_id: str, scene_id: str, take: int) -> Path:
        return (
            self._projects_root / episode_id / "downloads" / f"{scene_id}__take_{take:02d}.mp4"
        ).resolve()

    @staticmethod
    def _validate_segment(name: str, value: str) -> None:
        if not value or value in {".", ".."} or "/" in value or "\\" in value:
            raise InternalInvariantError(f"Unsafe {name}: {value!r}")
