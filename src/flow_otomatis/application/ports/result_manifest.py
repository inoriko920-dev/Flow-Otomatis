"""Output boundary for FLOW_OTOMATIS_RESULT.json."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from flow_otomatis.domain.result import ProjectResults


class ResultManifestWriterPort(Protocol):
    """Write one credential-free local result manifest."""

    def write(
        self, results: ProjectResults, *, recheck: Callable[[], ProjectResults] | None = None
    ) -> Path:
        """Publish only if the effective result still matches before atomic replace."""
        ...
