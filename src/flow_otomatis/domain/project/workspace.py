"""Imported project workspace state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene


@dataclass(frozen=True, slots=True)
class WorkspaceState:
    """Minimal real workspace persisted by STEP 10."""

    schema_version: str
    episode_id: str
    project_name: str
    source_package_path: str
    created_at: datetime
    imported_at: datetime
    model: str
    resolution: str
    aspect_ratio: str
    scenes: tuple[WorkspaceScene, ...]

    @property
    def ready_count(self) -> int:
        """Count scenes ready to execute after a duration has been selected."""

        return sum(scene.readiness is SceneReadiness.READY for scene in self.scenes)

    @property
    def duration_selection_count(self) -> int:
        """Count valid scenes waiting only for operator duration selection."""

        return sum(
            scene.readiness is SceneReadiness.NEEDS_DURATION_SELECTION for scene in self.scenes
        )

    @property
    def blocking_count(self) -> int:
        """Count scenes blocked by missing input or invalid duration."""

        non_blocking = {SceneReadiness.READY, SceneReadiness.NEEDS_DURATION_SELECTION}
        return sum(scene.readiness not in non_blocking for scene in self.scenes)
