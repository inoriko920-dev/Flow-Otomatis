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
        # The file itself can be a regular MP4 while an ancestor directory
        # was later replaced with an NTFS junction or a symlink. A persisted
        # success must not silently attest to bytes at a redirected location.
        canonical = candidate.resolve(strict=True)
        expected = Path(os.path.abspath(candidate))
        if os.path.normcase(str(canonical)) != os.path.normcase(str(expected)):
            return False
        with candidate.open("rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size <= 0:
                return False
            prefix = stream.read(512)
            if not prefix:
                return False
            # A browser can save its login page or an API error response
            # under a .mp4 filename. These are demonstrably not video bytes
            # and must never be attested as a downloaded result. This is a
            # narrow negative check, not a complete MP4 decoder.
            # Some server error pages begin with an HTML comment or are
            # encoded as UTF-16 instead of UTF-8. Neither can be accepted as
            # MP4 just because the browser named it .mp4.
            signatures = ("<!doctype html", "<html", "<?xml", "<!--", "{", "[")
            if prefix.startswith((b"\xff\xfe", b"\xfe\xff")):
                leading_text = prefix.decode("utf-16", errors="ignore").lstrip(
                    "\ufeff \t\r\n"
                ).lower()
                return not leading_text.startswith(signatures)
            leading = prefix.lstrip(b"\xef\xbb\xbf \t\r\n").lower()
            return not leading.startswith(tuple(sig.encode("ascii") for sig in signatures))
    except (OSError, RuntimeError, ValueError):
        return False
