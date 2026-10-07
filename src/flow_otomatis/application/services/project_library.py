"""Local Project Hub / recovery service for STEP 11 W11-02."""

from __future__ import annotations

from flow_otomatis.application.ports.workspace_repository import (
    WorkspaceRepositoryPort,
    WorkspaceScanResult,
)
from flow_otomatis.domain.errors import InternalInvariantError
from flow_otomatis.domain.project import WorkspaceState


class ProjectLibraryService:
    """Browse and reopen persisted local workspaces."""

    def __init__(self, workspace_repository: WorkspaceRepositoryPort) -> None:
        self._workspace_repository = workspace_repository

    def list_recent(self, limit: int = 10) -> tuple[WorkspaceState, ...]:
        """Return healthy local projects newest first."""

        if limit < 1:
            return ()
        return self._workspace_repository.list_recent(limit)

    def scan_recent(self, limit: int = 10) -> WorkspaceScanResult:
        """Return healthy projects plus isolated corrupt/unavailable entries."""

        if limit < 1:
            return WorkspaceScanResult(workspaces=(), issues=())
        return self._workspace_repository.scan_recent(limit)

    def open_project(self, episode_id: str) -> WorkspaceState:
        """Reload a persisted project for local recovery/open."""

        workspace = self._workspace_repository.load(episode_id)
        if workspace is None:
            raise InternalInvariantError(f"Project not found: {episode_id}")
        return workspace
