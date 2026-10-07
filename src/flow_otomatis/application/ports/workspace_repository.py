"""Application-owned persistence port for imported workspaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from flow_otomatis.domain.project import WorkspaceState


@dataclass(frozen=True, slots=True)
class WorkspaceReadIssue:
    """One local project that could not be decoded/opened during a library scan."""

    episode_id: str
    kind: Literal["CORRUPT", "UNAVAILABLE"]


@dataclass(frozen=True, slots=True)
class WorkspaceScanResult:
    """Healthy workspaces plus isolated local read issues."""

    workspaces: tuple[WorkspaceState, ...]
    issues: tuple[WorkspaceReadIssue, ...]


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
        """List most recently imported healthy local workspaces."""
        ...

    def scan_recent(self, limit: int = 10) -> WorkspaceScanResult:
        """List healthy workspaces while reporting isolated local read issues."""
        ...
