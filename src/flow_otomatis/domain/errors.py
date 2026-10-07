"""Domain/application error roots and normalized local failure types."""

from __future__ import annotations


class FlowOtomatisError(Exception):
    """Base error for known Flow-Otomatis failures."""


class InternalInvariantError(FlowOtomatisError):
    """Raised when an impossible application state is observed."""


class InvalidDurationError(FlowOtomatisError):
    """Target/selected duration violates the frozen Flow duration contract."""


class PackageValidationError(FlowOtomatisError):
    """Episode package or import manifest does not satisfy the contract."""

    def __init__(self, message: str, *, code: str = "PACKAGE_INVALID") -> None:
        super().__init__(message)
        self.code = code


class PackageSecurityError(FlowOtomatisError):
    """Episode package contains an unsafe path/archive structure."""


class StorageError(FlowOtomatisError):
    """Local project persistence failed."""
