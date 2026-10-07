"""Read-only Google Flow preflight application service."""

from __future__ import annotations

from flow_otomatis.application.ports.google_flow_preflight import (
    GoogleFlowAccessProbe,
    GoogleFlowPreflightPort,
)


class GoogleFlowPreflightService:
    """Expose Flow reachability checks without any mutating provider action."""

    def __init__(self, preflight: GoogleFlowPreflightPort) -> None:
        self._preflight = preflight

    def check(self, profile_id: str) -> GoogleFlowAccessProbe:
        """Perform one read-only Flow reachability/auth check."""

        return self._preflight.check(profile_id)

    def close(self, profile_id: str) -> None:
        """Close one profile context while preserving local session data."""

        self._preflight.close(profile_id)

    def shutdown(self) -> None:
        """Release browser resources."""

        self._preflight.shutdown()
