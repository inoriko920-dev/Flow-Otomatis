"""Durable local generation queue state and recovery evidence."""

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


class GenerationAttentionCode(StrEnum):
    """Machine-readable reason an automatic generation path is blocked."""

    REQUEST_STALE = "REQUEST_STALE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    SUBMIT_AMBIGUOUS = "SUBMIT_AMBIGUOUS"
    ORPHAN_PRE_SUBMIT = "ORPHAN_PRE_SUBMIT"
    ORPHAN_POSSIBLE_SUBMIT = "ORPHAN_POSSIBLE_SUBMIT"
    LEGACY_UNVERIFIED = "LEGACY_UNVERIFIED"
    LEGACY_RUNNING_UNVERIFIED = "LEGACY_RUNNING_UNVERIFIED"


@dataclass(frozen=True, slots=True)
class GenerationJob:
    """One durable serial generation job with an immutable prepared request snapshot."""

    job_id: str
    episode_id: str
    scene_id: str
    target_duration_s: float
    flow_duration_s: int
    state: GenerationJobState
    created_at: datetime
    updated_at: datetime
    image_file: str | None = None
    motion_prompt: str | None = None
    model: str | None = None
    resolution: str | None = None
    aspect_ratio: str | None = None
    request_fingerprint: str | None = None
    remote_result_id: str | None = None
    error_message: str | None = None
    attention_code: GenerationAttentionCode | None = None
    owner_id: str | None = None
    lease_expires_at: datetime | None = None
    submit_started_at: datetime | None = None

    @property
    def has_verified_request_snapshot(self) -> bool:
        """Return whether all provider request fields and a fingerprint were persisted."""

        return all(
            value is not None
            for value in (
                self.image_file,
                self.motion_prompt,
                self.model,
                self.resolution,
                self.aspect_ratio,
                self.request_fingerprint,
            )
        )
