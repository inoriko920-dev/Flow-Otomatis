"""Application-owned adapter ports."""

from flow_otomatis.application.ports.download_results import DownloadResultRepositoryPort
from flow_otomatis.application.ports.episode_package import (
    EpisodePackagePort,
    PackageSceneEvidence,
    PackageSnapshot,
)
from flow_otomatis.application.ports.generation_jobs import GenerationJobRepositoryPort
from flow_otomatis.application.ports.generation_provider import (
    GenerationAuthenticationRequiredError,
    GenerationCancelledError,
    GenerationProviderError,
    GenerationProviderPort,
    GenerationProviderResult,
    GenerationRequest,
    GenerationSubmissionAmbiguousError,
)
from flow_otomatis.application.ports.google_session import (
    GoogleSessionPort,
    GoogleSessionProfile,
    GoogleSessionState,
)
from flow_otomatis.application.ports.result_manifest import ResultManifestWriterPort
from flow_otomatis.application.ports.workspace_repository import WorkspaceRepositoryPort

__all__ = [
    "DownloadResultRepositoryPort",
    "EpisodePackagePort",
    "GenerationAuthenticationRequiredError",
    "GenerationCancelledError",
    "GenerationJobRepositoryPort",
    "GenerationProviderError",
    "GenerationProviderPort",
    "GenerationProviderResult",
    "GenerationRequest",
    "GenerationSubmissionAmbiguousError",
    "GoogleSessionPort",
    "GoogleSessionProfile",
    "GoogleSessionState",
    "PackageSceneEvidence",
    "PackageSnapshot",
    "ResultManifestWriterPort",
    "WorkspaceRepositoryPort",
]
