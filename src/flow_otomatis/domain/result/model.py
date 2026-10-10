"""Local result state. Generate and Download are deliberately separate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from flow_otomatis.domain.job import GenerationJobState


class DownloadState(str):
    """Stable string constants for local download state."""

    NOT_DOWNLOADED = "NOT_DOWNLOADED"
    DOWNLOADED = "DOWNLOADED"
    FAILED = "FAILED"
    ATTENTION_REQUIRED = "ATTENTION_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class DownloadRecord:
    """Persisted local download outcome for one Scene."""

    episode_id: str
    scene_id: str
    state: str
    updated_at: datetime
    output_path: str | None = None
    take: int = 1
    error_message: str | None = None
    generation_remote_result_id: str | None = None


@dataclass(frozen=True, slots=True)
class SceneResult:
    """Combined local view of one Scene's Generate and Download states."""

    scene_id: str
    target_duration_s: float
    selected_flow_duration_s: int | None
    trim_target_s: float
    generate_state: GenerationJobState | None
    remote_result_id: str | None
    download_state: str
    output_path: str | None
    take: int
    updated_at: datetime | None
    download_generation_result_id: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectResults:
    """Local Hasil snapshot for one persisted episode."""

    episode_id: str
    project_name: str
    model: str
    resolution: str
    aspect_ratio: str
    scenes: tuple[SceneResult, ...]

    @property
    def generated_count(self) -> int:
        return sum(scene.generate_state is GenerationJobState.GENERATED for scene in self.scenes)

    @property
    def downloaded_count(self) -> int:
        return sum(scene.download_state == DownloadState.DOWNLOADED for scene in self.scenes)

    @property
    def attention_count(self) -> int:
        return sum(
            scene.generate_state
            in {GenerationJobState.FAILED, GenerationJobState.ATTENTION_REQUIRED}
            or scene.download_state in {
                DownloadState.FAILED,
                DownloadState.UNAVAILABLE,
                DownloadState.ATTENTION_REQUIRED,
            }
            for scene in self.scenes
        )

    @property
    def handoff_ready(self) -> bool:
        # A persisted DOWNLOAD alone is insufficient evidence of a completed
        # Generate. Corrupt/out-of-order historical rows must never authorize
        # handoff to an editor without both confirmed stages for every Scene.
        return (
            bool(self.scenes)
            and self.generated_count == len(self.scenes)
            and self.downloaded_count == len(self.scenes)
        )
