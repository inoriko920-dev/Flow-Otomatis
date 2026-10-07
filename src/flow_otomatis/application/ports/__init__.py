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
    GenerationRequestValidationError,
    GenerationSubmissionAmbiguousError,
)
from flow_otomatis.application.ports.google_flow_preflight import (
    GoogleFlowAccessProbe,
    GoogleFlowAccessState,
    GoogleFlowPreflightPort,
)
from flow_otomatis.application.ports.google_session import (
    GoogleSessionCommandPort,
    GoogleSessionPort,
    GoogleSessionProfile,
    GoogleSessionRestartGate,
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
    "GenerationRequestValidationError",
    "GenerationSubmissionAmbiguousError",
    "GoogleFlowAccessProbe",
    "GoogleFlowAccessState",
    "GoogleFlowPreflightPort",
    "GoogleSessionCommandPort",
    "GoogleSessionPort",
    "GoogleSessionProfile",
    "GoogleSessionRestartGate",
    "GoogleSessionState",
    "PackageSceneEvidence",
    "PackageSnapshot",
    "ResultManifestWriterPort",
    "WorkspaceRepositoryPort",
]
