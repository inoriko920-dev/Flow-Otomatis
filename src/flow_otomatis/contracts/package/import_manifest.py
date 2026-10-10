"""Versioned FLOW_OTOMATIS_IMPORT.json contract."""

from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

FlowDuration = Literal[4, 6, 8, 10]


class ProductionProfile(BaseModel):
    """Locked biography production profile."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    model: Literal["Omni Flash 1.1"]
    resolution: Literal["720p"]
    aspect_ratio: Literal["16:9"]


class ImportScene(BaseModel):
    """One scene job from FLOW_OTOMATIS_IMPORT.json."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    scene_id: str = Field(pattern=r"^SCENE_\d{3}$")
    target_duration_s: float = Field(gt=0.0, le=10.0)
    recommended_flow_duration_s: FlowDuration
    selected_flow_duration_s: FlowDuration | None = None
    image_file: str = Field(min_length=1)
    motion_prompt: str = Field(min_length=1)
    model: Literal["Omni Flash 1.1"]
    resolution: Literal["720p"]
    aspect_ratio: Literal["16:9"]
    status: str = Field(min_length=1)
    trim_target_s: float = Field(gt=0.0, le=10.0)

    @model_validator(mode="after")
    def validate_timing(self) -> ImportScene:
        """Keep trim/selection consistent with authoritative target timing."""

        if abs(self.trim_target_s - self.target_duration_s) > 1e-6:
            raise ValueError("trim_target_s must match target_duration_s")
        if (
            self.selected_flow_duration_s is not None
            and self.selected_flow_duration_s + 1e-9 < self.target_duration_s
        ):
            raise ValueError("selected_flow_duration_s cannot be shorter than target")
        return self


class ImportManifest(BaseModel):
    """Top-level import manifest contract, schema version 1.0."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    schema_version: Literal["1.0"]
    episode_id: str = Field(pattern=r"^[A-Z0-9][A-Z0-9_-]{2,127}$")
    project_name: str = Field(min_length=1, max_length=200)
    production_profile: ProductionProfile
    scene_count: int = Field(ge=1)
    scenes: tuple[ImportScene, ...] = Field(min_length=1)
    created_at: AwareDatetime
    source_versions: dict[str, str]

    @model_validator(mode="after")
    def validate_scene_collection(self) -> ImportManifest:
        """Require a unique scene list whose declared count is truthful."""

        if self.scene_count != len(self.scenes):
            raise ValueError("scene_count does not match scenes length")
        scene_ids = [scene.scene_id for scene in self.scenes]
        if len(scene_ids) != len(set(scene_ids)):
            raise ValueError("scene_id values must be unique")
        return self
