"""Persistence port for durable local generation jobs."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Protocol

from flow_otomatis.domain.job import (
    GenerationAttentionCode,
    GenerationJob,
)


class GenerationJobRepositoryPort(Protocol):
    """Persist the serial generation queue and durable worker ownership evidence."""

    def ensure_jobs(self, jobs: Iterable[GenerationJob]) -> None:
        """Compatibility alias for explicitly preparing coherent Scene jobs."""
        ...

    def prepare_jobs(self, jobs: Iterable[GenerationJob]) -> None:
        """Insert or safely re-prepare nonterminal jobs without touching confirmed results."""
        ...

    def claim_next(
        self,
        episode_id: str,
        owner_id: str,
        *,
        lease_seconds: int,
        now: datetime | None = None,
    ) -> GenerationJob | None:
        """Atomically claim one verified QUEUED job under a durable owner lease."""
        ...

    def mark_submit_started(
        self,
        job_id: str,
        owner_id: str,
        *,
        lease_seconds: int,
        now: datetime | None = None,
    ) -> GenerationJob:
        """Persist the submit ambiguity boundary and renew the owner's lease."""
        ...

    def mark_generated(
        self,
        job_id: str,
        remote_result_id: str,
        owner_id: str,
    ) -> GenerationJob:
        """Persist successful Generate completion for the owning worker."""
        ...

    def mark_attention(
        self,
        job_id: str,
        error_message: str,
        attention_code: GenerationAttentionCode,
        owner_id: str,
    ) -> GenerationJob:
        """Persist an outcome that blocks automatic resubmission."""
        ...

    def mark_failed(
        self,
        job_id: str,
        error_message: str,
        owner_id: str,
    ) -> GenerationJob:
        """Persist a terminal failure proven safe to classify as failed."""
        ...

    def recover_expired(
        self,
        episode_id: str,
        *,
        now: datetime | None = None,
    ) -> tuple[GenerationJob, ...]:
        """Move only expired RUNNING leases to explicit attention states."""
        ...

    def list_for_episode(self, episode_id: str) -> tuple[GenerationJob, ...]:
        """Return durable jobs in deterministic creation order."""
        ...
