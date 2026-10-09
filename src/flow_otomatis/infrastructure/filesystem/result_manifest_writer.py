"""Atomic credential-free FLOW_OTOMATIS_RESULT.json writer."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import suppress
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.application.file_integrity import is_available_output
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.result import DownloadState, ProjectResults


class ResultManifestWriter:
    """Write handoff JSON below the user-scoped project directory."""

    def __init__(self, projects_root: Path) -> None:
        self._projects_root = projects_root

    def _verified_export_directory(self, episode_id: str) -> Path:
        """Reject redirected project/export parents, including Windows junctions."""

        if (
            not episode_id
            or episode_id in {".", ".."}
            or "/" in episode_id
            or "\\" in episode_id
            or "\x00" in episode_id
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

    def write(self, results: ProjectResults) -> Path:
        output_dir = self._verified_export_directory(results.episode_id)
        target = output_dir / "FLOW_OTOMATIS_RESULT.json"
        if target.is_symlink():
            raise InternalInvariantError("Result export target is a redirected file")

        # A file may vanish after snapshot(): recheck during export as well.
        verified_scenes = tuple(
            replace(scene, download_state=DownloadState.UNAVAILABLE)
            if scene.download_state == DownloadState.DOWNLOADED
            and not is_available_output(scene.output_path)
            else scene
            for scene in results.scenes
        )
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
            # being written. Fail closed before publishing outside the root.
            self._verified_export_directory(results.episode_id)
            if target.is_symlink():
                raise InternalInvariantError("Result export target was redirected")
            os.replace(temporary, target)
        finally:
            # Never delete a competing export's file or the previously
            # published manifest when write/flush/replace fails.
            if temporary is not None:
                with suppress(OSError):
                    temporary.unlink(missing_ok=True)
        return target
