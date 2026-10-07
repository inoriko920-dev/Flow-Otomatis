"""Provider-neutral boundary for downloading one generated media result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class MediaDownloadProviderError(RuntimeError):
    """Base error for a controlled provider download outcome."""


class MediaDownloadAuthenticationRequiredError(MediaDownloadProviderError):
    """The authorized provider session is no longer ready."""


class MediaDownloadAmbiguousError(MediaDownloadProviderError):
    """The provider may have started a download, but final file state is uncertain."""


class MediaDownloadCancelledError(MediaDownloadProviderError):
    """The download was cancelled before a confirmed final file existed."""


@dataclass(frozen=True, slots=True)
class GeneratedMediaDownloadRequest:
    """Provider-neutral request for one already-generated remote result."""

    episode_id: str
    scene_id: str
    remote_result_id: str
    destination_path: str


@dataclass(frozen=True, slots=True)
class GeneratedMediaDownloadResult:
    """Confirmed local file outcome returned by a download provider."""

    output_path: str


class GeneratedMediaDownloadProviderPort(Protocol):
    """Download one remote generated result without changing Generate state."""

    def download(
        self,
        request: GeneratedMediaDownloadRequest,
    ) -> GeneratedMediaDownloadResult:
        """Materialize one confirmed local result file."""
        ...
