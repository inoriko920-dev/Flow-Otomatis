"""Local generation queue state. External provider integration is STEP 12."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class GenerationJobState(StrEnum):
    """Durable local generation lifecycle before Download handling."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    GENERATED = "GENERATED"
    ATTENTION_REQUIRED = "ATTENTION_REQUIRED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class GenerationJob:
    """One durable serial generation job."""

    job_id: str
    episode_id: str
    scene_id: str
    target_duration_s: float
    flow_duration_s: int
    state: GenerationJobState
    created_at: datetime
    updated_at: datetime
    remote_result_id: str | None = None
    error_message: str | None = None
