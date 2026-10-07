"""Atomic credential-free FLOW_OTOMATIS_RESULT.json writer."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.domain.result import ProjectResults


class ResultManifestWriter:
    """Write handoff JSON below the user-scoped project directory."""

    def __init__(self, projects_root: Path) -> None:
        self._projects_root = projects_root

    def write(self, results: ProjectResults) -> Path:
        output_dir = self._projects_root / results.episode_id / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / "FLOW_OTOMATIS_RESULT.json"
        temporary = target.with_suffix(".json.tmp")

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
            "scene_count": len(results.scenes),
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
                for scene in results.scenes
            ],
        }
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, target)
        return target
