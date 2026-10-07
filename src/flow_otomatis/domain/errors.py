"""Domain/application error roots and normalized local failure types."""

from __future__ import annotations


class FlowOtomatisError(Exception):
    """Base error for known Flow-Otomatis failures."""


class InternalInvariantError(FlowOtomatisError):
    """Raised when an impossible application state is observed."""


class InvalidDurationError(FlowOtomatisError):
    """Target/selected duration violates the frozen Flow duration contract."""


class SceneNotFoundError(FlowOtomatisError):
    """Requested Scene ID is not present in the persisted workspace."""


class PackageValidationError(FlowOtomatisError):
    """Episode package or import manifest does not satisfy the contract."""

    def __init__(self, message: str, *, code: str = "PACKAGE_INVALID") -> None:
        super().__init__(message)
        self.code = code


class PackageSecurityError(FlowOtomatisError):
    """Episode package contains an unsafe path/archive structure."""


class WorkspaceAlreadyExistsError(FlowOtomatisError):
    """A new import tried to reuse an existing episode/project identity."""

    def __init__(self, episode_id: str) -> None:
        self.episode_id = episode_id
        super().__init__(f"Workspace already exists: {episode_id}")


class StorageError(FlowOtomatisError):
    """Local project persistence failed."""


class WorkspaceCorruptError(StorageError):
    """Persisted workspace rows cannot be decoded safely."""

    def __init__(self, episode_id: str) -> None:
        self.episode_id = episode_id
        super().__init__(f"Workspace data is corrupt: {episode_id}")
