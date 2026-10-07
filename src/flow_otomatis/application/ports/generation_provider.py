"""Provider boundary for one Scene generation request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """Provider-neutral request built from persisted Scene planning."""

    episode_id: str
    scene_id: str
    image_file: str
    motion_prompt: str
    target_duration_s: float
    flow_duration_s: int
    model: str
    resolution: str
    aspect_ratio: str


@dataclass(frozen=True, slots=True)
class GenerationProviderResult:
    """Minimal provider-neutral generation result."""

    remote_result_id: str


class GenerationProviderPort(Protocol):
    """Generate one Scene. Real external adapters belong to STEP 12."""

    def generate(self, request: GenerationRequest) -> GenerationProviderResult:
        """Submit/complete one generation according to adapter semantics."""
        ...
