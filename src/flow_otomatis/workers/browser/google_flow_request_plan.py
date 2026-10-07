"""Pure pre-submit validation and deterministic Google Flow request mapping."""

from __future__ import annotations

from dataclasses import dataclass

from flow_otomatis.application.ports.generation_provider import (
    GenerationRequest,
    GenerationRequestValidationError,
)

_ALLOWED_FLOW_DURATIONS = frozenset({4, 6, 8, 10})
_EXPECTED_MODEL = "Omni Flash 1.1"
_EXPECTED_RESOLUTION = "720p"
_EXPECTED_ASPECT_RATIO = "16:9"


@dataclass(frozen=True, slots=True)
class PreparedGoogleFlowRequest:
    """Validated immutable values that a live driver may later map to current Flow UI."""

    episode_id: str
    scene_id: str
    image_file: str
    motion_prompt: str
    target_duration_s: float
    flow_duration_s: int
    model: str
    resolution: str
    aspect_ratio: str


def prepare_google_flow_request(request: GenerationRequest) -> PreparedGoogleFlowRequest:
    """Validate the frozen project contract before any mutating browser action."""

    episode_id = request.episode_id.strip()
    scene_id = request.scene_id.strip()
    image_file = request.image_file.strip()
    motion_prompt = request.motion_prompt.strip()
    model = request.model.strip()
    resolution = request.resolution.strip()
    aspect_ratio = request.aspect_ratio.strip()

    if not episode_id:
        raise GenerationRequestValidationError("episode_id wajib tersedia sebelum submit Flow.")
    if not scene_id:
        raise GenerationRequestValidationError("scene_id wajib tersedia sebelum submit Flow.")
    if not image_file:
        raise GenerationRequestValidationError("File gambar Scene wajib tersedia sebelum submit Flow.")
    if not motion_prompt:
        raise GenerationRequestValidationError("Motion prompt wajib tersedia sebelum submit Flow.")
    if request.target_duration_s <= 0:
        raise GenerationRequestValidationError("Target durasi Scene harus lebih besar dari 0 detik.")
    if request.flow_duration_s not in _ALLOWED_FLOW_DURATIONS:
        raise GenerationRequestValidationError("Durasi Flow hanya boleh 4, 6, 8, atau 10 detik.")
    if request.target_duration_s > request.flow_duration_s:
        raise GenerationRequestValidationError(
            "Durasi Flow harus sama atau lebih panjang dari target Scene; pecah Scene >10 detik."
        )
    if model != _EXPECTED_MODEL:
        raise GenerationRequestValidationError(
            f"Model harus {_EXPECTED_MODEL}; diterima: {model or '<kosong>'}."
        )
    if resolution != _EXPECTED_RESOLUTION:
        raise GenerationRequestValidationError(
            f"Resolusi harus {_EXPECTED_RESOLUTION}; diterima: {resolution or '<kosong>'}."
        )
    if aspect_ratio != _EXPECTED_ASPECT_RATIO:
        raise GenerationRequestValidationError(
            f"Aspect ratio harus {_EXPECTED_ASPECT_RATIO}; diterima: {aspect_ratio or '<kosong>'}."
        )

    return PreparedGoogleFlowRequest(
        episode_id=episode_id,
        scene_id=scene_id,
        image_file=image_file,
        motion_prompt=motion_prompt,
        target_duration_s=request.target_duration_s,
        flow_duration_s=request.flow_duration_s,
        model=model,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
    )
