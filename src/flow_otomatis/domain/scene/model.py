"""Scene timing and readiness rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from flow_otomatis.domain.errors import InvalidDurationError

FLOW_DURATIONS: tuple[int, ...] = (4, 6, 8, 10)


class SceneReadiness(StrEnum):
    """Derived local readiness before any live provider work."""

    READY = "READY"
    NEEDS_DURATION_SELECTION = "NEEDS_DURATION_SELECTION"
    MISSING_IMAGE = "MISSING_IMAGE"
    MISSING_PROMPT = "MISSING_PROMPT"
    INVALID_DURATION = "INVALID_DURATION"


def recommend_flow_duration(target_duration_s: float) -> int:
    """Return the smallest supported Flow duration covering the exact target."""

    if target_duration_s <= 0.0 or target_duration_s > 10.0:
        raise InvalidDurationError(
            "Target duration must be greater than 0 and no more than 10 seconds"
        )
    for duration in FLOW_DURATIONS:
        if target_duration_s <= duration + 1e-9:
            return duration
    raise InvalidDurationError("No supported Flow duration covers the target")


def validate_selected_flow_duration(
    target_duration_s: float,
    selected_flow_duration_s: int,
) -> None:
    """Reject a user selection that cannot safely cover the exact Target."""

    recommend_flow_duration(target_duration_s)
    if selected_flow_duration_s not in FLOW_DURATIONS:
        raise InvalidDurationError("Flow duration must be one of 4, 6, 8, or 10 seconds")
    if selected_flow_duration_s + 1e-9 < target_duration_s:
        raise InvalidDurationError(
            "Selected Flow duration cannot be shorter than the authoritative Target"
        )


def derive_scene_readiness(
    *,
    target_duration_s: float,
    selected_flow_duration_s: int | None,
    image_exists: bool,
    motion_prompt: str,
) -> SceneReadiness:
    """Derive readiness without trusting manifest status text."""

    try:
        recommend_flow_duration(target_duration_s)
    except InvalidDurationError:
        return SceneReadiness.INVALID_DURATION

    if not image_exists:
        return SceneReadiness.MISSING_IMAGE
    if not motion_prompt.strip():
        return SceneReadiness.MISSING_PROMPT
    if selected_flow_duration_s is None:
        return SceneReadiness.NEEDS_DURATION_SELECTION
    try:
        validate_selected_flow_duration(target_duration_s, selected_flow_duration_s)
    except InvalidDurationError:
        return SceneReadiness.INVALID_DURATION
    return SceneReadiness.READY


@dataclass(frozen=True, slots=True)
class WorkspaceScene:
    """Real scene state used by workspace/persistence after import validation."""

    scene_id: str
    image_file: str
    image_exists: bool
    motion_prompt: str
    target_duration_s: float
    recommended_flow_duration_s: int
    selected_flow_duration_s: int | None
    readiness: SceneReadiness
    trim_target_s: float
    model: str
    resolution: str
    aspect_ratio: str
