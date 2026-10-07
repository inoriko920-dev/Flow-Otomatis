"""Persistence port for local download outcomes."""

from __future__ import annotations

from typing import Protocol

from flow_otomatis.domain.result import DownloadRecord


class DownloadResultRepositoryPort(Protocol):
    """Persist Download outcomes separately from Generate jobs."""

    def save(self, record: DownloadRecord) -> None:
        """Upsert one local download outcome."""
        ...

    def get(self, episode_id: str, scene_id: str) -> DownloadRecord | None:
        """Read one download outcome."""
        ...

    def list_for_episode(self, episode_id: str) -> tuple[DownloadRecord, ...]:
        """Read all local download outcomes for an episode."""
        ...
