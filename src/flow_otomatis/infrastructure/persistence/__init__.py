"""Persistence adapters."""

from flow_otomatis.infrastructure.persistence.sqlite_download_result_repository import (
    SqliteDownloadResultRepository,
)
from flow_otomatis.infrastructure.persistence.sqlite_gemini_key_repository import (
    SqliteGeminiKeyRepository,
)
from flow_otomatis.infrastructure.persistence.sqlite_generation_job_repository import (
    SqliteGenerationJobRepository,
)
from flow_otomatis.infrastructure.persistence.sqlite_workspace_repository import (
    SqliteWorkspaceRepository,
)

__all__ = [
    "SqliteDownloadResultRepository",
    "SqliteGeminiKeyRepository",
    "SqliteGenerationJobRepository",
    "SqliteWorkspaceRepository",
]
