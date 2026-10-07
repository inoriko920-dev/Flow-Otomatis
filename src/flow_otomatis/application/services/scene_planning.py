"""Local Scene planning commands for STEP 11 W11-01."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from flow_otomatis.application.ports.episode_package import EpisodePackagePort
from flow_otomatis.application.ports.workspace_repository import WorkspaceRepositoryPort
from flow_otomatis.domain.errors import InternalInvariantError, SceneNotFoundError
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import (
    WorkspaceScene,
    derive_scene_readiness,
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
        self._workspace_repository.save(workspace)
        persisted = self._workspace_repository.load(workspace.episode_id)
        if persisted is None:
            raise InternalInvariantError("Workspace update saved but reload returned no project")
        return persisted
