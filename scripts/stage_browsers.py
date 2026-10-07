"""Stage the exact Playwright Chromium runtime into a portable bundle root."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def stage_browser(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(destination.resolve())
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True,
        env=env,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        default=Path(".runtime/browsers"),
    )
    args = parser.parse_args()
    stage_browser(args.destination)
    print(f"Chromium staged at {args.destination.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
