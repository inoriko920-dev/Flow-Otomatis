"""Local Scene planning commands for STEP 11 W11-01."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from flow_otomatis.application.ports.episode_package import (
    EpisodeImageVerifierPort,
    EpisodePackagePort,
)
from flow_otomatis.application.ports.workspace_repository import WorkspaceRepositoryPort
from flow_otomatis.domain.errors import (
    InternalInvariantError,
    InvalidDurationError,
    PackageValidationError,
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
        *,
        image_verifier: EpisodeImageVerifierPort | None = None,
    ) -> None:
        self._package_reader = package_reader
        self._workspace_repository = workspace_repository
        self._image_verifier = image_verifier

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

    def preview_missing_recommended_durations(self, episode_id: str) -> tuple[tuple[str, int], ...]:
        """Show proposed local-only choices; never persist or contact the provider."""
        workspace = self.load_workspace(episode_id)
        return self._missing_duration_plan(workspace)

    def fill_missing_recommended_durations(
        self,
        episode_id: str,
        *,
        expected_workspace: WorkspaceState | None = None,
    ) -> WorkspaceState:
        """Update missing Flow selections, rejecting an outdated confirmation.

        Never override existing manual choices, source targets, trims, images,
        prompts, or pinned import SHA-256. Invalid targets stay unselected.
        If the operator supplied a preview snapshot, do not apply a newer
        workspace revision without a fresh confirmation.
        """
        workspace = self.load_workspace(episode_id)
        if expected_workspace is not None and workspace != expected_workspace:
            raise InternalInvariantError(
                "Workspace berubah setelah pratinjau durasi. "
                "Muat ulang proyek dan konfirmasi pilihan terbaru."
            )
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
        return self._save_and_reload(replace(workspace, scenes=updated), expected=workspace)

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
        evidence_by_id = {evidence.scene.scene_id: evidence for evidence in snapshot.scenes}
        scenes: list[WorkspaceScene] = []
        for scene in workspace.scenes:
            evidence = evidence_by_id.get(scene.scene_id)
            if evidence is not None and evidence.scene.image_file != scene.image_file:
                # A replaced manifest must not silently substitute a new source
                # image for the image approved at original import.
                raise PackageValidationError(
                    "Referensi gambar Scene berubah sejak impor; scan dibatalkan.",
                    code="IMAGE_REFERENCE_CHANGED",
                )
            exists = evidence is not None and evidence.image_exists
            if (
                exists
                and scene.image_sha256_imported is not None
                and self._image_verifier is not None
            ):
                try:
                    current_digest = self._image_verifier.image_digest(
                        Path(workspace.source_package_path), scene.scene_id, scene.image_file
                    )
                except Exception as exc:
                    raise PackageValidationError(
                        "Byte gambar tidak dapat diverifikasi; scan dibatalkan.",
                        code="IMAGE_VERIFICATION_FAILED",
                    ) from exc
                if current_digest != scene.image_sha256_imported:
                    raise PackageValidationError(
                        "Byte gambar berubah sejak impor; scan dibatalkan.",
                        code="IMAGE_CHANGED_SINCE_IMPORT",
                    )
            scenes.append(
                replace(
                    scene,
                    image_exists=exists,
                    readiness=derive_scene_readiness(
                        target_duration_s=scene.target_duration_s,
                        selected_flow_duration_s=scene.selected_flow_duration_s,
                        image_exists=exists,
                        motion_prompt=scene.motion_prompt,
                    ),
                )
            )
        return self._save_and_reload(
            replace(workspace, scenes=tuple(scenes)), expected=workspace
        )

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
        return self._save_and_reload(replace(workspace, scenes=scenes), expected=workspace)

    def _save_and_reload(
        self, workspace: WorkspaceState, *, expected: WorkspaceState
    ) -> WorkspaceState:
        self._workspace_repository.update(workspace, expected_workspace=expected)
        persisted = self._workspace_repository.load(workspace.episode_id)
        if persisted is None:
            raise InternalInvariantError("Workspace update saved but reload returned no project")
        return persisted
