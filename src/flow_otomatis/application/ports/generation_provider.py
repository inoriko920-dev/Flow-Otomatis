"""Provider boundary for one Scene generation request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class GenerationProviderError(RuntimeError):
    """Base error for a provider outcome that is safe to surface to the queue."""


class GenerationSafeFailureError(GenerationProviderError):
    """Proven rejection before provider acceptance; reprepare only by explicit command."""


class GenerationSubmissionAmbiguousError(GenerationProviderError):
    """The provider may have accepted a mutating submit; automatic retry is forbidden."""


class GenerationAuthenticationRequiredError(GenerationProviderError):
    """The selected authorized profile is no longer ready for generation."""


class GenerationCancelledError(GenerationProviderError):
    """The request was cancelled before any accepted submit was confirmed."""


class GenerationRequestValidationError(GenerationProviderError):
    """The request is invalid and must fail before any browser mutation occurs."""


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
    """Generate one Scene through an adapter with explicit submit semantics."""

    def generate(self, request: GenerationRequest) -> GenerationProviderResult:
        """Submit/complete one generation according to adapter semantics."""
        ...
