"""Canonical portable path resolution.

The application binary/resources may be portable, while user state and browser
sessions deliberately remain user-scoped. No feature module should derive these
roots independently.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PathService:
    """Resolved filesystem roots for one application process."""

    app_root: Path
    user_data_root: Path

    @classmethod
    def discover(
        cls,
        *,
        executable: Path | None = None,
        environ: Mapping[str, str] | None = None,
        home: Path | None = None,
    ) -> PathService:
        """Resolve roots without depending on the current working directory."""

        env = environ if environ is not None else os.environ
        exe = executable if executable is not None else Path(sys.executable)
        app_root = exe.resolve().parent if getattr(sys, "frozen", False) else _source_app_root()

        local_app_data = env.get("LOCALAPPDATA")
        if local_app_data:
            user_base = Path(local_app_data)
        else:
            user_home = home if home is not None else Path.home()
            user_base = user_home / "AppData" / "Local"

        return cls(
            app_root=app_root,
            user_data_root=(user_base / "Flow-Otomatis").resolve(),
        )

    @property
    def projects_root(self) -> Path:
        """Per-project durable state root."""

        return self.user_data_root / "Projects"

    @property
    def session_root(self) -> Path:
        """Sensitive browser-session root; never part of a project export."""

        return self.user_data_root / "Sessions"

    @property
    def log_root(self) -> Path:
        """Structured local log root."""

        return self.user_data_root / "Logs"

    @property
    def cache_root(self) -> Path:
        """Disposable app cache root."""

        return self.user_data_root / "Cache"

    @property
    def browser_runtime_root(self) -> Path:
        """Bundled Playwright browser runtime shipped beside the executable."""

        return self.app_root / "runtime" / "browsers"


def _source_app_root() -> Path:
    # path_service.py -> filesystem -> infrastructure -> flow_otomatis -> src -> repo
    return Path(__file__).resolve().parents[4]
