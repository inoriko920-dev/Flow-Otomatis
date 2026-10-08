"""Build the STEP 08 portable foundation artifact on Windows."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from importlib import metadata
from pathlib import Path

from flow_otomatis import __version__

PACKAGE_NAMES = ("PySide6", "playwright", "pydantic", "keyring", "PyInstaller")


def _git_head(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write_manifest(bundle_root: Path, repo_root: Path) -> None:
    manifest = {
        "app": "Flow-Otomatis",
        "app_version": __version__,
        "git_sha": os.environ.get("GITHUB_SHA") or _git_head(repo_root),
        "python": sys.version,
        "dependencies": {name: metadata.version(name) for name in PACKAGE_NAMES},
        "live_google_flow_tested": False,
    }
    (bundle_root / "BUILD_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _zip_bundle(bundle_root: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        for path in sorted(bundle_root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_root.parent))


def build(repo_root: Path, browser_source: Path) -> tuple[Path, Path]:
    dist_root = repo_root / "dist"
    work_root = repo_root / "build" / "pyinstaller"
    spec_root = repo_root / "build" / "spec"
    if dist_root.exists():
        shutil.rmtree(dist_root)
    if work_root.parent.exists():
        shutil.rmtree(work_root.parent)
    dist_root.mkdir(parents=True, exist_ok=True)
    work_root.mkdir(parents=True, exist_ok=True)
    spec_root.mkdir(parents=True, exist_ok=True)

    # Generate license provenance AFTER dist/ cleanup, otherwise build() removes
    # the notice created by an earlier CI step before packaging the release.
    notices_source = dist_root / "THIRD_PARTY_NOTICES.txt"
    subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "generate_third_party_notices.py"),
            str(notices_source),
        ],
        cwd=repo_root,
        check=True,
    )
    if not notices_source.is_file() or notices_source.stat().st_size == 0:
        raise RuntimeError("Third-party dependency notice was not generated")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onedir",
            "--windowed",
            "--name",
            "Flow-Otomatis",
            "--distpath",
            str(dist_root),
            "--workpath",
            str(work_root),
            "--specpath",
            str(spec_root),
            str(repo_root / "src" / "flow_otomatis" / "__main__.py"),
        ],
        cwd=repo_root,
        check=True,
    )

    bundle_root = dist_root / "Flow-Otomatis"
    if not bundle_root.exists():
        raise RuntimeError("PyInstaller did not create the expected onedir bundle")

    staged_browser = bundle_root / "runtime" / "browsers"
    staged_browser.parent.mkdir(parents=True, exist_ok=True)
    if not browser_source.exists():
        raise RuntimeError(f"Browser runtime is missing: {browser_source}")
    shutil.copytree(browser_source, staged_browser, dirs_exist_ok=True)

    shutil.copy2(notices_source, bundle_root / notices_source.name)

    _write_manifest(bundle_root, repo_root)

    zip_path = dist_root / "Flow-Otomatis-portable-win-x64.zip"
    _zip_bundle(bundle_root, zip_path)
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    checksum_path = dist_root / "SHA256SUMS.txt"
    checksum_path.write_text(
        f"{digest}  {zip_path.name}\n",
        encoding="utf-8",
    )
    return zip_path, checksum_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--browser-source",
        type=Path,
        default=Path(".runtime/browsers"),
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    zip_path, checksum_path = build(repo_root, args.browser_source.resolve())
    print(f"Built {zip_path}")
    print(f"Checksum file {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
