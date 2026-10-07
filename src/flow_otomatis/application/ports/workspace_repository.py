"""Application-owned persistence port for imported workspaces."""

from __future__ import annotations

from typing import Protocol

from flow_otomatis.domain.project import WorkspaceState


class WorkspaceRepositoryPort(Protocol):
    """Persist/reload minimal project workspace state."""

    def create(self, workspace: WorkspaceState) -> None:
        """Create a new workspace atomically; reject duplicate identity."""
        ...

    def update(self, workspace: WorkspaceState) -> None:
        """Update an already-persisted workspace transactionally."""
        ...

    def load(self, episode_id: str) -> WorkspaceState | None:
        """Load the latest persisted workspace for an episode."""
        ...

    def list_recent(self, limit: int = 10) -> tuple[WorkspaceState, ...]:
        """List most recently imported local workspaces."""
        ...
