"""Application-owned persistence port for imported workspaces."""

from __future__ import annotations

from typing import Protocol

from flow_otomatis.domain.project import WorkspaceState


class WorkspaceRepositoryPort(Protocol):
    """Persist/reload minimal project workspace state."""

    def save(self, workspace: WorkspaceState) -> None:
        """Store one workspace transactionally."""
        ...

    def load(self, episode_id: str) -> WorkspaceState | None:
        """Load the latest persisted workspace for an episode."""
        ...

    def list_recent(self, limit: int = 10) -> tuple[WorkspaceState, ...]:
        """List most recently imported local workspaces."""
        ...
