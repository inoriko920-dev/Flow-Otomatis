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

    def save_failure_if_unconfirmed(
        self, record: DownloadRecord, *, expected_remote_result_id: str | None = None
    ) -> None:
        """Never replace success/ambiguity; optionally verify browser Generate identity."""
        ...

    def save_attention_if_unconfirmed(
        self, record: DownloadRecord, *, expected_remote_result_id: str | None = None
    ) -> None:
        """Keep sticky ambiguity; optionally verify browser Generate identity."""
        ...

    def matches_current_generated_download(self, record: DownloadRecord) -> bool:
        """Read-only snapshot proving Download row and current Generate agree.

        Reuse must check both persisted facts together, not trust a previous
        job read that might have changed before returning a saved MP4.
        """
        ...

    def has_confirmed_manual_retry_authorization(self, record: DownloadRecord) -> bool:
        """Read-only proof that the current FAILED revision came from operator review.

        A leftover .part may coexist with a deliberately reviewed retry.
        Mere FAILED status or free-form error text is not authorization.
        """
        ...

    def reconcile_attention_for_retry(
        self,
        episode_id: str,
        scene_id: str,
        *,
        expected_remote_result_id: str,
        expected_updated_at: str,
    ) -> bool:
        """Atomically release one manually reviewed ambiguous Download.

        Implementations must match the current Generate identity and the exact
        ATTENTION_REQUIRED row revision, and append an audit entry. No file
        operations or browser retries are permitted here.
        """
        ...

    def get(self, episode_id: str, scene_id: str) -> DownloadRecord | None:
        """Read one download outcome."""
        ...

    def list_for_episode(self, episode_id: str) -> tuple[DownloadRecord, ...]:
        """Read all local download outcomes for an episode."""
        ...
