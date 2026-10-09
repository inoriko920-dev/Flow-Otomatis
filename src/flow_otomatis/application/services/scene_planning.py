"""Local Scene planning commands for STEP 11 W11-01."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from flow_otomatis.application.ports.episode_package import EpisodePackagePort
from flow_otomatis.application.ports.workspace_repository import WorkspaceRepositoryPort
from flow_otomatis.domain.errors import (
    InternalInvariantError,
    InvalidDurationError,
    SceneNotFoundError,
)
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import (
    WorkspaceScene,
    derive_scene_readiness,
    recommend_flow_duration,
    validate_selected_flow_duration,
)


class ScenePlanningService:
    """Persist duration choices and recompute local Scene readiness."""

    def __init__(
        self,
        package_reader: EpisodePackagePort,
        workspace_repository: WorkspaceRepositoryPort,
    ) -> None:
        self._package_reader = package_reader
        self._workspace_repository = workspace_repository

    def load_workspace(self, episode_id: str) -> WorkspaceState:
        """Load a persisted workspace or fail with a typed local invariant."""

        workspace = self._workspace_repository.load(episode_id)
        if workspace is None:
            raise InternalInvariantError(f"Workspace not found: {episode_id}")
        return workspace

    def select_flow_duration(
        self,
        episode_id: str,
        scene_id: str,
        duration_s: int,
    ) -> WorkspaceState:
        """Validate, persist, and reload one operator-selected Flow duration."""

        workspace = self.load_workspace(episode_id)
        scene = self._find_scene(workspace, scene_id)
        validate_selected_flow_duration(scene.target_duration_s, duration_s)
        updated_scene = replace(
            scene,
            selected_flow_duration_s=duration_s,
            readiness=derive_scene_readiness(
                target_duration_s=scene.target_duration_s,
                selected_flow_duration_s=duration_s,
                image_exists=scene.image_exists,
                motion_prompt=scene.motion_prompt,
            ),
        )
        return self._save_with_scene(workspace, updated_scene)

    def preview_missing_recommended_durations(
        self, episode_id: str
    ) -> tuple[tuple[str, int], ...]:
        """Show proposed local-only choices; never persist or contact the provider."""
        workspace = self.load_workspace(episode_id)
        return self._missing_duration_plan(workspace)

    def fill_missing_recommended_durations(self, episode_id: str) -> WorkspaceState:
        """Set only missing Flow selections in one durable update after user approval.

        Never override existing manual choices, Source Target, trims, images,
        prompts, or pinned import SHA-256. Invalid targets stay unselected.
        """
        workspace = self.load_workspace(episode_id)
        plan = dict(self._missing_duration_plan(workspace))
        if not plan:
            return workspace
        updated = tuple(
            replace(
                scene,
                selected_flow_duration_s=plan[scene.scene_id],
                readiness=derive_scene_readiness(
                    target_duration_s=scene.target_duration_s,
                    selected_flow_duration_s=plan[scene.scene_id],
                    image_exists=scene.image_exists,
                    motion_prompt=scene.motion_prompt,
                ),
            )
            if scene.scene_id in plan and scene.selected_flow_duration_s is None
            else scene
            for scene in workspace.scenes
        )
        return self._save_and_reload(replace(workspace, scenes=updated))

    @staticmethod
    def _missing_duration_plan(workspace: WorkspaceState) -> tuple[tuple[str, int], ...]:
        """Recalculate trusted ceil duration; skip invalid or duplicated IDs."""
        counts: dict[str, int] = {}
        for scene in workspace.scenes:
            counts[scene.scene_id] = counts.get(scene.scene_id, 0) + 1
        result: list[tuple[str, int]] = []
        for scene in workspace.scenes:
            if scene.selected_flow_duration_s is not None or counts[scene.scene_id] != 1:
                continue
            try:
                recommended = recommend_flow_duration(scene.target_duration_s)
            except InvalidDurationError:
                continue
            result.append((scene.scene_id, recommended))
        return tuple(result)

    def rescan_images(self, episode_id: str) -> WorkspaceState:
        """Re-read approved-image evidence from the original package source."""

        workspace = self.load_workspace(episode_id)
        snapshot = self._package_reader.load(Path(workspace.source_package_path))
        image_evidence = {
            evidence.scene.scene_id: evidence.image_exists for evidence in snapshot.scenes
        }

        scenes = tuple(
            replace(
                scene,
                image_exists=image_evidence.get(scene.scene_id, False),
                readiness=derive_scene_readiness(
                    target_duration_s=scene.target_duration_s,
                    selected_flow_duration_s=scene.selected_flow_duration_s,
                    image_exists=image_evidence.get(scene.scene_id, False),
                    motion_prompt=scene.motion_prompt,
                ),
            )
            for scene in workspace.scenes
        )
        return self._save_and_reload(replace(workspace, scenes=scenes))

    def _find_scene(self, workspace: WorkspaceState, scene_id: str) -> WorkspaceScene:
        for scene in workspace.scenes:
            if scene.scene_id == scene_id:
                return scene
        raise SceneNotFoundError(f"Scene not found: {scene_id}")

    def _save_with_scene(
        self,
        workspace: WorkspaceState,
        updated_scene: WorkspaceScene,
    ) -> WorkspaceState:
        scenes = tuple(
            updated_scene if scene.scene_id == updated_scene.scene_id else scene
            for scene in workspace.scenes
        )
        return self._save_and_reload(replace(workspace, scenes=scenes))

    def _save_and_reload(self, workspace: WorkspaceState) -> WorkspaceState:
        self._workspace_repository.update(workspace)
        persisted = self._workspace_repository.load(workspace.episode_id)
        if persisted is None:
            raise InternalInvariantError("Workspace update saved but reload returned no project")
        return persisted
