"""Safe generated-media download orchestration for STEP 12 I12-03A."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.application.file_integrity import is_available_output
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
        # Validate the project output root even on an idempotent read. A
        # historical DOWNLOADED row must not bypass redirected-folder checks.
        destination = self._destination_path(episode_id, scene_id, normalized_take)

        existing = self._download_repository.get(episode_id, scene_id)
        if (
            existing is not None
            and existing.state == DownloadState.DOWNLOADED
            and existing.output_path is not None
        ):
            existing_path = Path(existing.output_path).expanduser().absolute()
            if (
                existing.take == normalized_take
                and existing_path == destination
                and is_available_output(str(existing_path))
            ):
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

        destination.parent.mkdir(parents=True, exist_ok=True)
        # Recheck after directory creation: a redirected parent cannot be
        # accepted as the published result folder even if it appeared late.
        if self._destination_path(episode_id, scene_id, normalized_take) != destination:
            raise InternalInvariantError("Project download destination changed unexpectedly.")
        if destination.is_symlink() or destination.exists():
            raise InternalInvariantError(
                "Download destination already exists and will not be overwritten; "
                f"manual reconciliation required: {destination.name}"
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
            # A losing concurrent attempt must not erase a successful download.
            self._download_repository.save_failure_if_unconfirmed(record)
            raise

        # Validate the exact published file path, not a canonicalized
        # symlink target. The Browser Worker is not a trusted filesystem
        # authority, and no redirected target may be persisted as DOWNLOADED.
        output = Path(result.output_path).expanduser().absolute()
        # A malicious directory swap after the Browser Worker returned must
        # never be persisted as a completed local download.
        if self._destination_path(episode_id, scene_id, normalized_take) != destination:
            raise InternalInvariantError("Project download destination changed unexpectedly.")
        if output != destination:
            raise InternalInvariantError("Download provider returned an unexpected output path.")
        if not is_available_output(str(output)):
            raise InternalInvariantError(
                "Download provider did not produce a readable nonempty regular file."
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
        # Do not resolve away an existing symlink/junction before checking it.
        # Otherwise downloads/ -> another folder becomes an apparently valid
        # canonical destination outside this application's project.
        root = self._projects_root.expanduser().absolute()
        project = root / episode_id
        directory = project / "downloads"
        try:
            if any(node.is_symlink() or node.is_junction() for node in (root, project, directory)):
                raise InternalInvariantError(
                    "Project download directory is redirected; manual reconciliation required."
                )
            canonical_root = root.resolve()
            if (
                project.resolve() != canonical_root / episode_id
                or directory.resolve() != canonical_root / episode_id / "downloads"
            ):
                raise InternalInvariantError(
                    "Project download path escaped its configured project root."
                )
        except (OSError, RuntimeError, ValueError) as exc:
            raise InternalInvariantError(
                "Project download directory cannot be safely verified."
            ) from exc
        return directory / f"{scene_id}__take_{take:02d}.mp4"

    @staticmethod
    def _validate_segment(name: str, value: str) -> None:
        if not value or value in {".", ".."} or "/" in value or "\\" in value:
            raise InternalInvariantError(f"Unsafe {name}: {value!r}")
