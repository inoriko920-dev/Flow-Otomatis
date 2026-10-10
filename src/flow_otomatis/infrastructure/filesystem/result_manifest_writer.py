"""Atomic credential-free FLOW_OTOMATIS_RESULT.json writer."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable
from contextlib import suppress
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.application.file_integrity import is_available_output
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.job import GenerationJobState
from flow_otomatis.domain.result import DownloadState, ProjectResults


class ResultManifestWriter:
    """Write handoff JSON below the user-scoped project directory."""

    def __init__(self, projects_root: Path) -> None:
        self._projects_root = projects_root

    def _verified_export_directory(self, episode_id: str) -> Path:
        """Reject redirected project/export parents, including Windows junctions."""

        # This direct writer boundary must enforce the same Windows-safe
        # episode naming rules as the Download and SQLite boundaries.
        # Reject devices and control characters before creating any folder.
        forbidden = '<>:"/\\\\|?*'
        reserved = (
            {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
            | {f"COM{i}" for i in range(1, 10)}
            | {f"LPT{i}" for i in range(1, 10)}
        )
        if (
            not isinstance(episode_id, str)
            or not episode_id
            or episode_id in {".", ".."}
            or episode_id.endswith((".", " "))
            or any(char in forbidden or ord(char) < 32 for char in episode_id)
            or episode_id.split(".", 1)[0].upper() in reserved
        ):
            raise InternalInvariantError("Unsafe episode identity for result export")

        root = self._projects_root.expanduser()
        project = root / episode_id
        exports = project / "exports"
        # Validate every component before allowing creation in the next one.
        # Path.resolve(strict=True) detects NTFS junctions as well as symlinks.
        for directory in (root, project, exports):
            try:
                directory.mkdir(parents=True, exist_ok=True)
                canonical = directory.resolve(strict=True)
                expected = Path(os.path.abspath(directory))
                if (
                    not directory.is_dir()
                    or directory.is_symlink()
                    or os.path.normcase(str(canonical)) != os.path.normcase(str(expected))
                ):
                    raise InternalInvariantError(
                        "Result export directory redirects outside its project"
                    )
            except (OSError, RuntimeError, ValueError) as exc:
                raise InternalInvariantError(
                    "Result export directory cannot be safely verified"
                ) from exc
        return exports

    def write(self, results: ProjectResults, *, recheck: Callable[[], bool] | None = None) -> Path:
        output_dir = self._verified_export_directory(results.episode_id)
        target = output_dir / "FLOW_OTOMATIS_RESULT.json"
        if target.is_symlink():
            raise InternalInvariantError("Result export target is a redirected file")

        # A file may vanish after snapshot(): recheck during export as well.
        verified_scenes = tuple(
            replace(scene, download_state=DownloadState.UNAVAILABLE)
            if scene.download_state == DownloadState.DOWNLOADED
            and (
                scene.generate_state is not GenerationJobState.GENERATED
                or not (scene.remote_result_id or "").strip()
                or scene.download_generation_result_id != (scene.remote_result_id or "").strip()
                or not is_available_output(scene.output_path)
            )
            else scene
            for scene in results.scenes
        )

        # A published MP4 can be replaced while this manifest is being
        # serialized. The output status alone is not enough: remember its
        # filesystem identity and modification metadata before staging.
        def output_signature(path: str | None) -> tuple[int, int, int, int, int] | None:
            if not path or not is_available_output(path):
                return None
            try:
                info = os.stat(path, follow_symlinks=False)
            except OSError, RuntimeError, ValueError:
                return None
            return (
                info.st_dev,
                info.st_ino,
                info.st_size,
                info.st_mtime_ns,
                info.st_ctime_ns,
            )

        signatures: dict[str, tuple[int, int, int, int, int]] = {}
        for scene in verified_scenes:
            if scene.download_state == DownloadState.DOWNLOADED:
                signature = output_signature(scene.output_path)
                if signature is None:
                    raise InternalInvariantError(
                        "Manifest MP4 changed before export; manual reconciliation required."
                    )
                signatures[scene.scene_id] = signature

        payload = {
            "schema_version": "1.0",
            "episode_id": results.episode_id,
            "project_name": results.project_name,
            "generated_at": datetime.now(UTC).isoformat(),
            "production_profile": {
                "model": results.model,
                "resolution": results.resolution,
                "aspect_ratio": results.aspect_ratio,
            },
            "scene_count": len(verified_scenes),
            "scenes": [
                {
                    "scene_id": scene.scene_id,
                    "target_duration_s": scene.target_duration_s,
                    "selected_flow_duration_s": scene.selected_flow_duration_s,
                    "trim_target_s": scene.trim_target_s,
                    "generate_status": (
                        scene.generate_state.value
                        if scene.generate_state is not None
                        else "NOT_QUEUED"
                    ),
                    "remote_result_id": scene.remote_result_id,
                    "download_status": scene.download_state,
                    "output_path": scene.output_path,
                    "take": scene.take,
                    "updated_at": (
                        scene.updated_at.isoformat() if scene.updated_at is not None else None
                    ),
                }
                for scene in verified_scenes
            ],
        }
        # A fixed .json.tmp name races with another exporter. Each attempt owns
        # a private temporary beside the final manifest for atomic same-volume
        # publication. The existing final is never touched before publication.
        serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        # Remember the actual directory identity, not just a pathname. If
        # another process redirects/renames the parent during export, cleanup
        # must never delete an unrelated same-named file at the new path.
        initial_dir_stat = output_dir.stat()
        initial_dir_identity = (initial_dir_stat.st_dev, initial_dir_stat.st_ino)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=output_dir,
                prefix=".FLOW_OTOMATIS_RESULT.",
                suffix=".json.tmp",
                delete=False,
            ) as output:
                temporary = Path(output.name)
                output.write(serialized)
                output.flush()
                os.fsync(output.fileno())
            # A project directory may have changed while the temp file was
            # being written. Revalidating the *path* is not enough: a renamed
            # exports directory can be replaced by another ordinary directory
            # at the same path. The attempt must not publish into that new
            # directory or overwrite another manifest.
            self._verified_export_directory(results.episode_id)
            try:
                publish_dir_stat = output_dir.stat()
            except (OSError, RuntimeError, ValueError) as exc:
                raise InternalInvariantError(
                    "Result export directory changed before publication"
                ) from exc
            if (publish_dir_stat.st_dev, publish_dir_stat.st_ino) != initial_dir_identity:
                raise InternalInvariantError(
                    "Result export directory identity changed; preserve temporary for review"
                )
            if target.is_symlink():
                raise InternalInvariantError("Result export target was redirected")
            # Re-read SQLite/Scene/source through the owning service AFTER
            # writing and syncing the temporary JSON. Never publish a success
            # that belonged to an older Download/Generate revision.
            if recheck is not None and not recheck():
                raise InternalInvariantError(
                    "Result history changed during manifest export; "
                    "previous manifest and MP4 retained for reconciliation."
                )
            # Also reject filesystem changes that leave the same effective
            # Download status, including a replaced nonempty MP4.
            for scene in verified_scenes:
                if scene.download_state == DownloadState.DOWNLOADED and (
                    output_signature(scene.output_path) != signatures[scene.scene_id]
                ):
                    raise InternalInvariantError(
                        "Manifest MP4 changed during export; "
                        "previous manifest and video retained for reconciliation."
                    )
            os.replace(temporary, target)
        finally:
            # Do not follow a redirected parent during cleanup. When the
            # directory is renamed while writing, preserve the private .tmp
            # alongside the original manifest for explicit manual recovery.
            if temporary is not None:
                with suppress(OSError, RuntimeError, ValueError):
                    current_stat = output_dir.stat()
                    current_identity = (current_stat.st_dev, current_stat.st_ino)
                    canonical = output_dir.resolve(strict=True)
                    expected = Path(os.path.abspath(output_dir))
                    if (
                        current_identity == initial_dir_identity
                        and not output_dir.is_symlink()
                        and os.path.normcase(str(canonical)) == os.path.normcase(str(expected))
                    ):
                        temporary.unlink(missing_ok=True)
        return target
