"""Persistence port for local download outcomes."""

from __future__ import annotations

from typing import Protocol

from flow_otomatis.domain.result import DownloadRecord


class DownloadResultRepositoryPort(Protocol):
    """Persist Download outcomes separately from Generate jobs."""

    def save(self, record: DownloadRecord) -> None:
        """Upsert one local download outcome."""
        ...

    def save_if_current_generate(
        self, record: DownloadRecord, expected_remote_result_id: str
    ) -> bool:
        """Atomically save DOWNLOADED only if the matching Generate result is current.

        The Generate check and Download upsert must run inside one serialized
        database transaction; a prior read cannot satisfy this contract.
        """
        ...

    def save_failure_if_unconfirmed(self, record: DownloadRecord) -> None:
        """Never replace a success or unresolved ambiguous outcome with failure."""
        ...

    def save_attention_if_unconfirmed(self, record: DownloadRecord) -> None:
        """Persist a sticky ambiguous outcome without clobbering prior success/attention."""
        ...

    def get(self, episode_id: str, scene_id: str) -> DownloadRecord | None:
        """Read one download outcome."""
        ...

    def list_for_episode(self, episode_id: str) -> tuple[DownloadRecord, ...]:
        """Read all local download outcomes for an episode."""
        ...
