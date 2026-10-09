"""Read-only verification of local output bytes for effective download status."""

from __future__ import annotations

import os
import stat
from pathlib import Path


def is_available_output(output_path: str | None) -> bool:
    """Accept only a readable, nonempty regular file; never mutate the source."""

    if not output_path:
        return False
    candidate = Path(output_path)
    if not candidate.is_absolute():
        return False
    try:
        # A symbolic link can redirect a stored result to an unrelated file.
        # Reject it before reading, including after a previously valid output
        # is replaced while the application is running.
        if candidate.is_symlink():
            return False
        with candidate.open("rb") as stream:
            info = os.fstat(stream.fileno())
            return stat.S_ISREG(info.st_mode) and info.st_size > 0 and bool(stream.read(1))
    except OSError, ValueError:
        return False
