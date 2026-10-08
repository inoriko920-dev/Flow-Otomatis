"""Deterministic Google Flow result-download adapter contract for I12-03A.

This module deliberately contains no live selectors. The future live Browser Worker
driver must prove the current authorized Flow UI before it can implement download_one.
"""

from __future__ import annotations

import os
from contextlib import suppress
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from flow_otomatis.application.ports.generated_media_download import (
    GeneratedMediaDownloadRequest,
    GeneratedMediaDownloadResult,
    MediaDownloadAmbiguousError,
    MediaDownloadAuthenticationRequiredError,
    MediaDownloadCancelledError,
    MediaDownloadProviderError,
)


class GoogleFlowDownloadState(StrEnum):
    """Sanitized outcome of exactly one Browser Worker download attempt."""

    DOWNLOADED = "DOWNLOADED"
    SAFE_FAILURE = "SAFE_FAILURE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    CANCELLED = "CANCELLED"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True, slots=True)
class GoogleFlowDownloadEvidence:
    """Credential-free evidence returned by a future live Flow download driver."""

    state: GoogleFlowDownloadState
    detail: str
    output_path: str | None = None


class GoogleFlowDownloadDriver(Protocol):
    """Browser-owned seam; live selector implementation is intentionally deferred."""

    def download_one(
        self,
        profile_id: str,
        remote_result_id: str,
        destination_path: str,
        *,
        timeout_ms: int,
    ) -> GoogleFlowDownloadEvidence:
        """Attempt one download to the supplied temporary path; never retry silently."""
        ...


class GoogleFlowDownloadProvider:
    """Map one deterministic Browser Worker download attempt to a confirmed local file."""

    def __init__(
        self,
        profile_id: str,
        driver: GoogleFlowDownloadDriver,
        *,
        timeout_ms: int = 120_000,
    ) -> None:
        if timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")
        self._profile_id = profile_id
        self._driver = driver
        self._timeout_ms = timeout_ms

    def download(
        self,
        request: GeneratedMediaDownloadRequest,
    ) -> GeneratedMediaDownloadResult:
        """Perform exactly one driver download and atomically publish the final file."""

        remote_result_id = request.remote_result_id.strip()
        if not remote_result_id:
            raise MediaDownloadProviderError("Remote result identifier is empty.")

        final_path = Path(request.destination_path).expanduser().absolute()
        if os.path.lexists(final_path):
            raise MediaDownloadProviderError(
                "Final download path already exists and will not be overwritten."
            )
        # One attempt owns exactly one unpredictable partial path.
        # The worker may create this absent path but may never share another attempt's file.
        partial_path = final_path.with_name(f"{final_path.name}.{uuid4().hex}.part")
        if os.path.lexists(partial_path):
            raise MediaDownloadProviderError(
                "Unique partial path collision; nothing was overwritten."
            )

        evidence = self._driver.download_one(
            self._profile_id,
            remote_result_id,
            str(partial_path),
            timeout_ms=self._timeout_ms,
        )
        detail = evidence.detail[:500]

        if evidence.state is GoogleFlowDownloadState.DOWNLOADED:
            reported = Path(evidence.output_path or "").expanduser().resolve()
            if reported != partial_path:
                raise MediaDownloadAmbiguousError(
                    "Flow reported download success at an unexpected path."
                )
            if not partial_path.is_file() or partial_path.stat().st_size <= 0:
                raise MediaDownloadAmbiguousError(
                    "Flow reported download success without a non-empty file."
                )
            final_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                # NTFS CreateHardLinkW / POSIX link: fails atomically if final already exists.
                # Partial and final share the same parent and therefore filesystem.
                os.link(partial_path, final_path)
            except FileExistsError as exc:
                # Both the other owner's final file and our own partial are preserved.
                raise MediaDownloadProviderError(
                    "Final download appeared during this attempt; "
                    "the existing file is preserved. Inspect the partial before retrying."
                ) from exc
            except OSError as exc:
                # Never fall back to os.replace/copy-and-delete: the filesystem must
                # support a proven no-clobber primitive, otherwise stop safely.
                raise MediaDownloadAmbiguousError(
                    "Atomic no-overwrite publication failed; partial preserved "
                    "for manual recovery. No automatic retry is allowed."
                ) from exc
            # The final link is safely published; cleanup only this attempt's partial.
            with suppress(OSError):
                partial_path.unlink()
            return GeneratedMediaDownloadResult(output_path=str(final_path))

        if evidence.state is GoogleFlowDownloadState.AUTH_REQUIRED:
            raise MediaDownloadAuthenticationRequiredError(
                detail or "Google session requires manual login."
            )
        if evidence.state is GoogleFlowDownloadState.CANCELLED:
            raise MediaDownloadCancelledError(detail or "Download was cancelled safely.")
        if evidence.state is GoogleFlowDownloadState.AMBIGUOUS:
            raise MediaDownloadAmbiguousError(
                detail or "Flow download outcome is ambiguous; automatic retry is forbidden."
            )
        raise MediaDownloadProviderError(detail or "Google Flow download failed safely.")
