"""Persistence port for durable local generation jobs."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from flow_otomatis.domain.job import GenerationJob


class GenerationJobRepositoryPort(Protocol):
    """Persist the serial R1 generation queue."""

    def ensure_jobs(self, jobs: Iterable[GenerationJob]) -> None:
        """Insert missing jobs without duplicating existing Scene jobs."""
        ...

    def claim_next(self, episode_id: str) -> GenerationJob | None:
        """Atomically claim one QUEUED job if no RUNNING job exists."""
        ...

    def mark_generated(self, job_id: str, remote_result_id: str) -> GenerationJob:
        """Persist successful Generate completion."""
        ...

    def mark_attention(self, job_id: str, error_message: str) -> GenerationJob:
        """Persist an ambiguous/auth outcome that blocks automatic resubmission."""
        ...

    def mark_failed(self, job_id: str, error_message: str) -> GenerationJob:
        """Persist terminal local/provider failure."""
        ...

    def list_for_episode(self, episode_id: str) -> tuple[GenerationJob, ...]:
        """Return durable jobs in deterministic creation order."""
        ...
