"""Deterministic Google Flow result-download adapter contract for I12-03A.

This module deliberately contains no live selectors. The future live Browser Worker
driver must prove the current authorized Flow UI before it can implement download_one.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

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

        final_path = Path(request.destination_path).expanduser().resolve()
        if final_path.exists():
            raise MediaDownloadProviderError(
                "Final download path already exists and will not be overwritten."
            )
        partial_path = final_path.with_name(final_path.name + ".part")
        if partial_path.exists():
            raise MediaDownloadProviderError(
                "A partial download already exists; inspect it before retrying."
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
            os.replace(partial_path, final_path)
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
