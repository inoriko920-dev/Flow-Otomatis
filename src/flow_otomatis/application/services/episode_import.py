"""SLC-001 application service: validate package and create a real workspace."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.application.ports.episode_package import EpisodePackagePort
from flow_otomatis.application.ports.workspace_repository import WorkspaceRepositoryPort
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import (
    WorkspaceScene,
    derive_scene_readiness,
    recommend_flow_duration,
)


class EpisodeImportService:
    """Orchestrate package validation, domain derivation, and persistence."""

    def __init__(
        self,
        package_reader: EpisodePackagePort,
        workspace_repository: WorkspaceRepositoryPort,
    ) -> None:
        self._package_reader = package_reader
        self._workspace_repository = workspace_repository

    def validate(self, source_path: Path) -> WorkspaceState:
        """Validate a package and build real, not-yet-persisted workspace state."""

        snapshot = self._package_reader.load(source_path)
        manifest = snapshot.manifest
        scenes: list[WorkspaceScene] = []

        for evidence in snapshot.scenes:
            source_scene = evidence.scene
            recommended = recommend_flow_duration(source_scene.target_duration_s)
            readiness = derive_scene_readiness(
                target_duration_s=source_scene.target_duration_s,
                selected_flow_duration_s=source_scene.selected_flow_duration_s,
                image_exists=evidence.image_exists,
                motion_prompt=evidence.motion_prompt,
            )
            scenes.append(
                WorkspaceScene(
                    scene_id=source_scene.scene_id,
                    image_file=source_scene.image_file,
                    image_exists=evidence.image_exists,
                    motion_prompt=evidence.motion_prompt,
                    target_duration_s=source_scene.target_duration_s,
                    recommended_flow_duration_s=recommended,
                    selected_flow_duration_s=source_scene.selected_flow_duration_s,
                    readiness=readiness,
                    trim_target_s=source_scene.trim_target_s,
                    model=source_scene.model,
                    resolution=source_scene.resolution,
                    aspect_ratio=source_scene.aspect_ratio,
                )
            )

        return WorkspaceState(
            schema_version=manifest.schema_version,
            episode_id=manifest.episode_id,
            project_name=manifest.project_name,
            source_package_path=str(snapshot.source_path),
            created_at=manifest.created_at,
            imported_at=datetime.now(UTC),
            model=manifest.production_profile.model,
            resolution=manifest.production_profile.resolution,
            aspect_ratio=manifest.production_profile.aspect_ratio,
            scenes=tuple(scenes),
        )

    def create_workspace(self, workspace: WorkspaceState) -> WorkspaceState:
        """Persist a validated draft and reload it as the canonical saved state."""

        self._workspace_repository.create(workspace)
        persisted = self._workspace_repository.load(workspace.episode_id)
        if persisted is None:
            raise InternalInvariantError("Workspace save completed but reload returned no project")
        return persisted

    def import_package(self, source_path: Path) -> WorkspaceState:
        """Convenience path for non-interactive callers/tests."""

        return self.create_workspace(self.validate(source_path))
