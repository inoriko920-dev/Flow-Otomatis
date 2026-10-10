"""Safe generated-media download orchestration for STEP 12 I12-03A."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.application.file_integrity import is_available_output
from flow_otomatis.application.ports.download_results import DownloadResultRepositoryPort
from flow_otomatis.application.ports.generated_media_download import (
    GeneratedMediaDownloadProviderPort,
    GeneratedMediaDownloadRequest,
    MediaDownloadAmbiguousError,
    MediaDownloadAuthenticationRequiredError,
    MediaDownloadCancelledError,
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

        # A historical MP4/SQLite DOWNLOADED row alone cannot authorize
        # reuse. Recheck the current Generate state before any idempotent
        # return, including when the remote job has since been invalidated.
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

        existing = self._download_repository.get(episode_id, scene_id)
        if existing is not None and existing.state == DownloadState.ATTENTION_REQUIRED:
            raise InternalInvariantError(
                "Prior Download outcome is ambiguous; manual reconciliation required "
                "before another provider attempt."
            )
        if (
            existing is not None
            and existing.state == DownloadState.DOWNLOADED
            and existing.output_path is not None
        ):
            existing_path = Path(existing.output_path).expanduser().absolute()
            if (
                existing.take == normalized_take
                and existing.generation_remote_result_id == remote_result_id
                and existing_path == destination
                and is_available_output(str(existing_path))
            ):
                if not self._download_repository.matches_current_generated_download(existing):
                    raise InternalInvariantError(
                        "Cached Download no longer matches current Generate and persisted "
                        "Download identity; manual reconciliation required."
                    )
                return existing

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
            # Providers and browser drivers may include session URLs, tokens
            # or filesystem paths in their error text. Persist only our
            # fixed classification, never untrusted exception messages.
            if isinstance(exc, MediaDownloadAmbiguousError):
                safe_error = "Download outcome uncertain; manual reconciliation required."
            elif isinstance(exc, MediaDownloadAuthenticationRequiredError):
                safe_error = "Google session requires manual login."
            elif isinstance(exc, MediaDownloadCancelledError):
                safe_error = "Download was cancelled before a confirmed local file existed."
            else:
                safe_error = "Google Flow download failed; review the provider before retry."
            record = DownloadRecord(
                episode_id=episode_id,
                scene_id=scene_id,
                state=(
                    DownloadState.ATTENTION_REQUIRED
                    if isinstance(exc, MediaDownloadAmbiguousError)
                    else DownloadState.FAILED
                ),
                updated_at=datetime.now(UTC),
                take=normalized_take,
                error_message=safe_error,
                generation_remote_result_id=remote_result_id,
            )
            # Ambiguity is sticky: do not silently re-attempt a possibly
            # completed browser download or erase a successful rival record.
            if record.state == DownloadState.ATTENTION_REQUIRED:
                self._download_repository.save_attention_if_unconfirmed(record)
            else:
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
        # The Generate job may be invalidated while the browser worker is
        # downloading. A completed MP4 is not authorization to persist an old
        # remote result after its job has been requeued or changed.
        current_jobs = {
            item.scene_id: item for item in self._job_repository.list_for_episode(episode_id)
        }
        current_job = current_jobs.get(scene_id)
        if (
            current_job is None
            or current_job.state is not GenerationJobState.GENERATED
            or (current_job.remote_result_id or "").strip() != remote_result_id
        ):
            # Never delete an MP4 that was already published: recovery is an
            # explicit operator reconciliation, not an automatic retry.
            raise InternalInvariantError(
                "Generate result changed during Download; local video needs reconciliation."
            )

        record = DownloadRecord(
            episode_id=episode_id,
            scene_id=scene_id,
            state=DownloadState.DOWNLOADED,
            updated_at=datetime.now(UTC),
            output_path=str(output),
            take=normalized_take,
            generation_remote_result_id=remote_result_id,
        )
        if not self._download_repository.save_if_current_generate(record, remote_result_id):
            # The result changed after the second read but before commit.
            # Keep the MP4 bytes and historical rows for manual reconciliation.
            raise InternalInvariantError(
                "Generate result changed during atomic Download save; "
                "local video needs reconciliation."
            )
        return record

    def release_retry_after_manual_review(
        self,
        episode_id: str,
        scene_id: str,
        *,
        expected_remote_result_id: str,
        expected_updated_at: str,
        reviewed_provider_and_local_files: bool,
    ) -> DownloadRecord:
        """Explicitly unlock one ambiguous attempt; never retry automatically.

        A reviewer must independently inspect provider outcome, published MP4,
        and partial files. This method performs only an atomic SQLite transition
        and audit insertion. It never downloads, moves, deletes or attests MP4.
        """

        if reviewed_provider_and_local_files is not True:
            raise InternalInvariantError(
                "Manual provider and local-file review is required before Download retry."
            )
        self._validate_segment("episode_id", episode_id)
        self._validate_segment("scene_id", scene_id)
        existing = self._download_repository.get(episode_id, scene_id)
        if (
            existing is None
            or existing.state != DownloadState.ATTENTION_REQUIRED
            or existing.generation_remote_result_id != expected_remote_result_id
            or existing.updated_at.isoformat() != expected_updated_at
            or existing.output_path is not None
        ):
            raise InternalInvariantError(
                "Ambiguous Download evidence changed; review the current result again."
            )
        # Never clear ambiguity when a canonical MP4 has already appeared.
        # It may be the download's missing success evidence and must be
        # reconciled separately instead of permitting another provider call.
        destination = self._destination_path(episode_id, scene_id, existing.take)
        if os.path.lexists(destination):
            raise InternalInvariantError(
                "Download destination exists; reconcile the existing MP4 before retry."
            )
        if not self._download_repository.reconcile_attention_for_retry(
            episode_id,
            scene_id,
            expected_remote_result_id=expected_remote_result_id,
            expected_updated_at=expected_updated_at,
        ):
            raise InternalInvariantError(
                "Generate or Download changed during reconciliation; retry is not authorized."
            )
        updated = self._download_repository.get(episode_id, scene_id)
        if updated is None:
            raise InternalInvariantError("Reconciled Download history is unavailable.")
        return updated

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
        """Reject path traversal and Windows ADS/device aliases before I/O."""

        forbidden = '<>:"/\\|?*'
        device = value.split(".", 1)[0].upper()
        reserved = (
            {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
            | {f"COM{i}" for i in range(1, 10)}
            | {f"LPT{i}" for i in range(1, 10)}
        )
        if (
            not value
            or value in {".", ".."}
            or value.endswith((".", " "))
            or any(character in forbidden or ord(character) < 32 for character in value)
            or device in reserved
        ):
            raise InternalInvariantError(f"Unsafe {name}: {value!r}")
