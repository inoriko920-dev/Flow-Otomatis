"""Smoke-test the packaged Windows foundation from a foreign CWD."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def smoke(bundle_root: Path) -> None:
    exe = bundle_root / "Flow-Otomatis.exe"
    manifest_path = bundle_root / "BUILD_MANIFEST.json"
    browser_root = bundle_root / "runtime" / "browsers"

    if not exe.is_file():
        raise RuntimeError(f"Missing executable: {exe}")
    if not manifest_path.is_file():
        raise RuntimeError(f"Missing build manifest: {manifest_path}")
    if not browser_root.is_dir() or not any(browser_root.iterdir()):
        raise RuntimeError("Bundled Chromium runtime directory is empty")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("app") != "Flow-Otomatis":
        raise RuntimeError("Unexpected build manifest application identity")

    with tempfile.TemporaryDirectory(prefix="Flow Otomatis ünicode ") as foreign_cwd:
        completed = subprocess.run(
            [str(exe.resolve())],
            cwd=foreign_cwd,
            timeout=30,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"Portable executable exited with {completed.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "bundle_root",
        nargs="?",
        type=Path,
        default=Path("dist/Flow-Otomatis"),
    )
    args = parser.parse_args()
    smoke(args.bundle_root.resolve())
    print("Portable foundation smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
