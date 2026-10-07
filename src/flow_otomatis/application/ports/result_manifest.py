"""Output boundary for FLOW_OTOMATIS_RESULT.json."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from flow_otomatis.domain.result import ProjectResults


class ResultManifestWriterPort(Protocol):
    """Write one credential-free local result manifest."""

    def write(self, results: ProjectResults) -> Path:
        """Atomically write FLOW_OTOMATIS_RESULT.json and return its path."""
        ...
