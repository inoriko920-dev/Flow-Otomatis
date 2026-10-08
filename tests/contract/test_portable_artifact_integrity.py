"""Release ZIP verification regressions: run offline without real Google login."""

from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from pathlib import Path

import pytest
from scripts.verify_portable_artifact import (
    PortableArtifactError,
    _check_member,
    verify_portable_artifact,
)

_SHA = "a" * 40
_REQUIRED_FILES = {
    "Flow-Otomatis/Flow-Otomatis.exe": b"test executable",
    "Flow-Otomatis/THIRD_PARTY_NOTICES.txt": b"license inventory",
    "Flow-Otomatis/runtime/browsers/chromium-000/chrome-win64/chrome.exe": b"browser",
}


def _manifest(**overrides: object) -> bytes:
    fields: dict[str, object] = {
        "app": "Flow-Otomatis",
        "app_version": "0.1.0",
        "git_sha": _SHA,
        "live_google_flow_tested": False,
        "dependencies": {},
    }
    fields.update(overrides)
    return json.dumps(fields).encode("utf-8")


def _release(
    tmp_path: Path,
    *,
    removed: str | None = None,
    additions: list[tuple[str | zipfile.ZipInfo, bytes]] | None = None,
    manifest: bytes | None = None,
) -> tuple[Path, Path]:
    archive_path = tmp_path / "Flow-Otomatis-portable-win-x64.zip"
    members = dict(_REQUIRED_FILES)
    members["Flow-Otomatis/BUILD_MANIFEST.json"] = _manifest() if manifest is None else manifest
    if removed is not None:
        members.pop(removed)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as archive:
        for path, data in members.items():
            archive.writestr(path, data)
        for path, data in additions or []:
            archive.writestr(path, data)
    return archive_path, _checksum(archive_path)


def _checksum(path: Path) -> Path:
    checksum = path.parent / "SHA256SUMS.txt"
    checksum.write_text(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n",
        encoding="ascii",
    )
    return checksum


def test_portable_integrity_accepts_expected_source_and_full_payload(tmp_path: Path) -> None:
    archive, checksum = _release(tmp_path)
    report = verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)
    assert report.source_sha == _SHA
    assert report.entry_count == 4
    assert report.sha256 == hashlib.sha256(archive.read_bytes()).hexdigest()


def test_portable_integrity_rejects_tampered_distribution_checksum(tmp_path: Path) -> None:
    archive, checksum = _release(tmp_path)
    checksum.write_text(f"{'0' * 64}  {archive.name}\n", encoding="ascii")
    with pytest.raises(PortableArtifactError, match="does not match"):
        verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        ({"git_sha": "b" * 40}, "source SHA"),
        ({"app": "Different-App"}, "application identity"),
        ({"live_google_flow_tested": True}, "live-test claim"),
    ],
)
def test_portable_integrity_rejects_false_build_manifest_claims(
    tmp_path: Path, overrides: dict[str, object], error: str
) -> None:
    archive, checksum = _release(tmp_path, manifest=_manifest(**overrides))
    with pytest.raises(PortableArtifactError, match=error):
        verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)


@pytest.mark.parametrize(
    "removed",
    [
        "Flow-Otomatis/Flow-Otomatis.exe",
        "Flow-Otomatis/THIRD_PARTY_NOTICES.txt",
        "Flow-Otomatis/BUILD_MANIFEST.json",
        "Flow-Otomatis/runtime/browsers/chromium-000/chrome-win64/chrome.exe",
    ],
)
def test_portable_integrity_rejects_incomplete_bundle(tmp_path: Path, removed: str) -> None:
    archive, checksum = _release(tmp_path, removed=removed)
    with pytest.raises(PortableArtifactError, match="missing"):
        verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)


@pytest.mark.parametrize(
    "bad_name",
    [
        "Flow-Otomatis/../outside.txt",
        "Flow-Otomatis/../../outside.txt",
        "Flow-Otomatis/CON.txt",
        "Flow-Otomatis/SCENE:alternate.txt",
        "Flow-Otomatis/path. /video.mp4",
        "/Flow-Otomatis/absolute.txt",
        "unrelated/other.txt",
    ],
)
def test_portable_integrity_rejects_unsafe_paths(tmp_path: Path, bad_name: str) -> None:
    archive, checksum = _release(tmp_path, additions=[(bad_name, b"unsafe")])
    with pytest.raises(PortableArtifactError, match="Unsafe"):
        verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)


def test_portable_integrity_rejects_case_insensitive_duplicate(tmp_path: Path) -> None:
    archive, checksum = _release(
        tmp_path,
        additions=[("flow-otomatis/flow-otomatis.exe", b"another executable")],
    )
    with pytest.raises(PortableArtifactError, match="Unsafe|duplicate"):
        verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)


def test_portable_integrity_rejects_symlink_entry(tmp_path: Path) -> None:
    link = zipfile.ZipInfo("Flow-Otomatis/runtime/magic-link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    archive, checksum = _release(tmp_path, additions=[(link, b"../../outside")])
    with pytest.raises(PortableArtifactError, match="symlinks"):
        verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)


def test_portable_integrity_rejects_crc_corruption_even_with_valid_sha(
    tmp_path: Path,
) -> None:
    archive, _checksum_path = _release(tmp_path)
    original = archive.read_bytes()
    assert original.count(b"test executable") == 1
    archive.write_bytes(original.replace(b"test executable", b"evil executable"))
    checksum = _checksum(archive)
    with pytest.raises(PortableArtifactError, match="CRC|corrupt"):
        verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)


def test_portable_integrity_rejects_truncated_zip_even_when_hash_matches(
    tmp_path: Path,
) -> None:
    archive, _checksum_path = _release(tmp_path)
    archive.write_bytes(archive.read_bytes()[:90])
    checksum = _checksum(archive)
    with pytest.raises(PortableArtifactError, match="corrupt"):
        verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)


def test_portable_integrity_rejects_invalid_source_sha(tmp_path: Path) -> None:
    archive, checksum = _release(tmp_path)
    with pytest.raises(PortableArtifactError, match="40 lowercase"):
        verify_portable_artifact(archive, checksum, expected_git_sha="not-a-commit")


def test_portable_integrity_rejects_checksum_for_different_zip(tmp_path: Path) -> None:
    archive, checksum = _release(tmp_path)
    checksum.write_text(f"{'0' * 64}  OTHER.zip\n", encoding="ascii")
    with pytest.raises(PortableArtifactError, match="name exactly"):
        verify_portable_artifact(archive, checksum, expected_git_sha=_SHA)


def test_portable_path_validator_rejects_raw_windows_backslash() -> None:
    # ZipInfo normalizes native backslashes to "/" during normal Windows ZIP
    # decoding; exercise the canonical name guard with an unnormalized entry.
    member = zipfile.ZipInfo("Flow-Otomatis/placeholder.txt")
    member.filename = r"Flow-Otomatis\bad.txt"
    with pytest.raises(PortableArtifactError, match="Unsafe"):
        _check_member(member, set())
