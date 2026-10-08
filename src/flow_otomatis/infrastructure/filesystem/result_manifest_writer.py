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
from flow_otomatis.domain.result import DownloadState, ProjectResults


class ResultManifestWriter:
    """Write handoff JSON below the user-scoped project directory."""

    def __init__(self, projects_root: Path) -> None:
        self._projects_root = projects_root

    def write(self, results: ProjectResults) -> Path:
        output_dir = self._projects_root / results.episode_id / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / "FLOW_OTOMATIS_RESULT.json"

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
            os.replace(temporary, target)
        finally:
            # Never delete a competing export's file or the previously
            # published manifest when write/flush/replace fails.
            if temporary is not None:
                with suppress(OSError):
                    temporary.unlink(missing_ok=True)
        return target
