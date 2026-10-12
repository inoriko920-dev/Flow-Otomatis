"""Read-only Google Flow preflight application service."""

from __future__ import annotations

from concurrent.futures import Future

from flow_otomatis.application.ports.google_flow_preflight import (
    GoogleFlowAccessProbe,
    GoogleFlowPreflightPort,
)
from flow_otomatis.application.ports.google_session import GoogleSessionCommandPort


class GoogleFlowPreflightService:
    """Expose read-only Flow checks via the session's browser owner."""

    def __init__(
        self,
        preflight: GoogleFlowPreflightPort,
        *,
        commands: GoogleSessionCommandPort | None = None,
    ) -> None:
        self._preflight = preflight
        self._commands = commands

    def check(self, profile_id: str) -> GoogleFlowAccessProbe:
        """Synchronous adapter access for non-Qt callers and fixture tests."""

        return self._preflight.check(profile_id)

    def check_async(self, profile_id: str) -> Future[GoogleFlowAccessProbe]:
        """Enqueue on the same browser worker that owns Google session handles."""

        if self._commands is not None:
            return self._commands.submit_check_flow(profile_id)
        result: Future[GoogleFlowAccessProbe] = Future()
        try:
            result.set_result(self._preflight.check(profile_id))
        except Exception as exc:
            result.set_exception(exc)
        return result

    def close(self, profile_id: str) -> None:
        """Close a browser context in non-Qt adapter/test code only."""

        self._preflight.close(profile_id)

    def shutdown(self) -> None:
        """Release the read-only adapter in non-Qt adapter/test code only."""

        self._preflight.shutdown()
