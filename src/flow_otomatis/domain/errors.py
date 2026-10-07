"""Domain-level error roots."""


class FlowOtomatisError(Exception):
    """Base error for known Flow-Otomatis failures."""


class InternalInvariantError(FlowOtomatisError):
    """Raised when an impossible application state is observed."""
