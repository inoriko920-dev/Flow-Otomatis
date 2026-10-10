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

from flow_otomatis.application.file_integrity import is_available_output
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
        # The service checks its project root; the provider also rejects an
        # immediate redirected download folder when invoked through another
        # adapter, including NTFS junctions on Windows.
        if final_path.parent.is_symlink() or final_path.parent.is_junction():
            raise MediaDownloadProviderError(
                "Download destination folder is redirected; nothing was written."
            )
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

        try:
            evidence = self._driver.download_one(
                self._profile_id,
                remote_result_id,
                str(partial_path),
                timeout_ms=self._timeout_ms,
            )
        except MediaDownloadProviderError as exc:
            if os.path.lexists(partial_path) and not isinstance(exc, MediaDownloadAmbiguousError):
                raise MediaDownloadAmbiguousError(
                    "Flow driver left a partial file after reporting failure; "
                    "inspect the preserved file before any retry."
                ) from exc
            raise
        except Exception as exc:
            # After a browser attempt starts, an unexpected driver crash or
            # timeout cannot prove that no remote/local transfer occurred.
            # Preserve any partial file, never retry, and avoid saving raw
            # exception text (which may contain private browser/session data).
            raise MediaDownloadAmbiguousError(
                "Flow browser attempt stopped unexpectedly; the outcome is "
                "uncertain and requires manual reconciliation before retry."
            ) from exc
        detail = evidence.detail[:500]

        if evidence.state is GoogleFlowDownloadState.DOWNLOADED:
            # Do not call resolve() before verifying the driver's original
            # path: a symlink could mask an unrelated file as our partial.
            reported = Path(evidence.output_path or "").expanduser().absolute()
            if reported != partial_path:
                raise MediaDownloadAmbiguousError(
                    "Flow reported download success at an unexpected path."
                )
            if not is_available_output(str(partial_path)):
                raise MediaDownloadAmbiguousError(
                    "Flow reported download success without a readable, nonempty regular file."
                )
            final_path.parent.mkdir(parents=True, exist_ok=True)
            # The worker is asynchronous; recheck the parent before publishing
            # in case an external actor swapped it during the download.
            if final_path.parent.is_symlink() or final_path.parent.is_junction():
                raise MediaDownloadAmbiguousError(
                    "Download destination folder changed during the attempt; "
                    "partial preserved for manual recovery."
                )
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

        # A driver cannot certify SAFE_FAILURE, CANCELLED or AUTH_REQUIRED
        # if it has already written an attempt-owned partial: the local
        # outcome requires reconciliation before a future browser retry.
        if (
            os.path.lexists(partial_path)
            and evidence.state is not GoogleFlowDownloadState.AMBIGUOUS
        ):
            raise MediaDownloadAmbiguousError(
                "Flow left a partial file despite an unconfirmed outcome; "
                "inspect the preserved file before any retry."
            )

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
