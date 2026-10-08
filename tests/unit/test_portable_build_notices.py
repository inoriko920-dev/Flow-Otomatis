"""Offline regression for third-party notices surviving dist cleanup and ZIP creation."""

from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

import pytest

from scripts import build_portable
from scripts.verify_portable_artifact import verify_portable_artifact

_GIT = "b" * 40


def _fake_dist_build(
    repo_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    write_notice: bool,
) -> Path:
    browser_root = repo_root / "browser_stage"
    chrome = browser_root / "chromium-123" / "chrome-win64" / "chrome.exe"
    chrome.parent.mkdir(parents=True)
    chrome.write_bytes(b"chrome-synthetic")

    def fake_run(command: list[str], *, cwd: Path, check: bool) -> subprocess.CompletedProcess[str]:
        assert cwd == repo_root
        assert check
        if "generate_third_party_notices.py" in str(command[1]):
            if write_notice:
                Path(command[-1]).write_text(
                    "Flow-Otomatis - fresh dependency provenance",
                    encoding="utf-8",
                )
        elif "PyInstaller" in command:
            packaged = repo_root / "dist" / "Flow-Otomatis"
            packaged.mkdir(parents=True)
            (packaged / "Flow-Otomatis.exe").write_bytes(b"dummy-executable")
        else:
            raise AssertionError(f"Unexpected build subprocess: {command!r}")
        return subprocess.CompletedProcess(command, 0)

    def write_manifest(bundle_root: Path, _repo_root: Path) -> None:
        (bundle_root / "BUILD_MANIFEST.json").write_text(
            json.dumps(
                {
                    "app": "Flow-Otomatis",
                    "git_sha": _GIT,
                    "live_google_flow_tested": False,
                }
            ),
            encoding="utf-8",
        )

    monkeypatch.setattr(build_portable.subprocess, "run", fake_run)
    monkeypatch.setattr(build_portable, "_write_manifest", write_manifest)
    return browser_root


def test_portable_build_regenerates_notices_after_removing_old_dist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    old_dist = repo_root / "dist"
    old_dist.mkdir(parents=True)
    (old_dist / "THIRD_PARTY_NOTICES.txt").write_text("stale notice", encoding="utf-8")
    browser = _fake_dist_build(repo_root, monkeypatch, write_notice=True)

    archive, checksum = build_portable.build(repo_root, browser)
    assert checksum.is_file()
    with zipfile.ZipFile(archive) as zip_file:
        assert zip_file.read("Flow-Otomatis/THIRD_PARTY_NOTICES.txt") == (
            b"Flow-Otomatis - fresh dependency provenance"
        )
    report = verify_portable_artifact(archive, checksum, expected_git_sha=_GIT)
    assert report.sha256 == hashlib.sha256(archive.read_bytes()).hexdigest()


def test_portable_build_stops_when_dependency_notice_cannot_be_generated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    browser = _fake_dist_build(repo_root, monkeypatch, write_notice=False)
    with pytest.raises(RuntimeError, match="notice was not generated"):
        build_portable.build(repo_root, browser)
    assert not (repo_root / "dist" / "Flow-Otomatis-portable-win-x64.zip").exists()
