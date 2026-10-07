"""Safe AI Agent request/response domain objects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class GeminiAgentAction(StrEnum):
    """Review-only action proposals. None of these execute automatically."""

    NONE = "NONE"
    REVIEW_SCENE = "REVIEW_SCENE"
    OPEN_RESULTS = "OPEN_RESULTS"
    OPEN_GOOGLE_PROFILES = "OPEN_GOOGLE_PROFILES"
    DOWNLOAD_SCENE = "DOWNLOAD_SCENE"


@dataclass(frozen=True, slots=True)
class GeminiAgentContext:
    """Credential-free local context supplied to Gemini."""

    episode_id: str
    project_name: str
    scene_id: str
    scene_readiness: str
    target_duration_s: float
    flow_duration_s: int | None
    image_available: bool


@dataclass(frozen=True, slots=True)
class GeminiAgentReply:
    """Sanitized assistant response plus a non-executing proposal."""

    message: str
    action: GeminiAgentAction = GeminiAgentAction.NONE
    target_scene_id: str | None = None
    rationale: str = ""

    @property
    def display_text(self) -> str:
        """Render a compact Indonesian result without implying action execution."""

        text = self.message.strip()
        if self.action is GeminiAgentAction.NONE:
            return text
        target = f" • {self.target_scene_id}" if self.target_scene_id else ""
        rationale = f"\nAlasan: {self.rationale.strip()}" if self.rationale.strip() else ""
        return (
            f"{text}\n\nUsulan tindakan: {self.action.value}{target}"
            f"{rationale}\nBelum dijalankan otomatis."
        )
