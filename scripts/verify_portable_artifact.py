"""Verify the actual distributable Windows ZIP, not just its extracted build tree.

Fail closed on wrong checksums, bad CRCs, unsafe entries, unexpected build
identity, or incomplete portable runtime. This uses only Python stdlib.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

_ROOT = "Flow-Otomatis/"
_REQUIRED = {
    _ROOT + "Flow-Otomatis.exe",
    _ROOT + "BUILD_MANIFEST.json",
    _ROOT + "THIRD_PARTY_NOTICES.txt",
}
_HASH_LINE = re.compile(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)\n?")
_GIT_SHA = re.compile(r"[0-9a-f]{40}")
_MAX_ENTRIES = 100_000
_MAX_EXTRACTED_BYTES = 16 * 1024**3
_WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class PortableArtifactError(ValueError):
    """The output ZIP is unsafe, corrupted, incomplete or mismatched."""


@dataclass(frozen=True, slots=True)
class PortableArtifactReport:
    """Credential-free release integrity evidence."""

    sha256: str
    entry_count: int
    source_sha: str


def _check_member(info: zipfile.ZipInfo, seen: set[str]) -> None:
    name = info.filename
    if (
        not name
        or name.startswith("/")
        or "\\" in name
        or "\x00" in name
        or not name.startswith(_ROOT)
        or ":" in name
    ):
        raise PortableArtifactError(f"Unsafe ZIP member: {name!r}")

    components = name.rstrip("/").split("/")
    if any(
        component in {"", ".", ".."}
        or component.endswith((".", " "))
        or component.split(".", maxsplit=1)[0].upper() in _WINDOWS_RESERVED
        for component in components
    ):
        raise PortableArtifactError(f"Unsafe Windows ZIP member: {name!r}")

    canonical = str(PurePosixPath(name)).casefold()
    if canonical in seen:
        raise PortableArtifactError(f"Ambiguous duplicate Windows ZIP member: {name!r}")
    seen.add(canonical)

    unix_mode = info.external_attr >> 16
    if info.create_system == 3 and stat.S_IFMT(unix_mode) == stat.S_IFLNK:
        raise PortableArtifactError(f"ZIP symlinks are not permitted: {name!r}")
    if info.flag_bits & 1:
        raise PortableArtifactError(f"Encrypted ZIP member is not permitted: {name!r}")


def _expected_checksum(zip_path: Path, checksum_path: Path) -> str:
    try:
        raw = checksum_path.read_text(encoding="ascii")
    except OSError as exc:
        raise PortableArtifactError("Portable SHA256SUMS.txt could not be read") from exc
    match = _HASH_LINE.fullmatch(raw)
    if match is None or match.group(2) != zip_path.name:
        raise PortableArtifactError("SHA256SUMS.txt must name exactly this ZIP")
    return match.group(1)


def verify_portable_artifact(
    zip_path: Path,
    checksum_path: Path,
    *,
    expected_git_sha: str,
) -> PortableArtifactReport:
    """Verify checksum, ZIP CRC, path safety and expected release contents."""

    if _GIT_SHA.fullmatch(expected_git_sha) is None:
        raise PortableArtifactError("Expected source commit must be 40 lowercase hex characters")
    declared_hash = _expected_checksum(zip_path, checksum_path)
    sha256 = hashlib.sha256()
    try:
        with zip_path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                sha256.update(chunk)
    except OSError as exc:
        raise PortableArtifactError("Portable ZIP could not be read") from exc
    actual_hash = sha256.hexdigest()
    if declared_hash != actual_hash:
        raise PortableArtifactError("Portable ZIP SHA-256 does not match SHA256SUMS.txt")

    try:
        with zipfile.ZipFile(zip_path) as archive:
            infos = archive.infolist()
            if not infos or len(infos) > _MAX_ENTRIES:
                raise PortableArtifactError("Portable ZIP entry count is invalid")
            if sum(info.file_size for info in infos) > _MAX_EXTRACTED_BYTES:
                raise PortableArtifactError("Portable ZIP exceeds extraction size limit")
            seen: set[str] = set()
            filenames: set[str] = set()
            for info in infos:
                _check_member(info, seen)
                if not info.is_dir():
                    filenames.add(info.filename)
            if missing := _REQUIRED - filenames:
                raise PortableArtifactError(
                    f"Portable ZIP missing required file: {sorted(missing)}"
                )
            if not any(
                name.startswith(_ROOT + "runtime/browsers/")
                and name.lower().endswith("/chrome.exe")
                for name in filenames
            ):
                raise PortableArtifactError("Portable ZIP is missing staged Chromium executable")
            manifest_bytes = archive.read(_ROOT + "BUILD_MANIFEST.json")
            manifest = json.loads(manifest_bytes.decode("utf-8"))
            if not isinstance(manifest, dict):
                raise PortableArtifactError("Portable build manifest must be an object")
            if manifest.get("app") != "Flow-Otomatis":
                raise PortableArtifactError("Unexpected portable application identity")
            if manifest.get("git_sha") != expected_git_sha:
                raise PortableArtifactError("Portable manifest source SHA differs from CI source")
            if manifest.get("live_google_flow_tested") is not False:
                raise PortableArtifactError(
                    "Portable manifest makes an unsupported live-test claim"
                )
            if archive.testzip() is not None:
                raise PortableArtifactError("Portable ZIP contains a member with invalid CRC")
    except zipfile.BadZipFile as exc:
        raise PortableArtifactError("Portable ZIP container or member CRC is corrupt") from exc
    except UnicodeError as exc:
        raise PortableArtifactError("Portable manifest is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise PortableArtifactError("Portable manifest JSON is invalid") from exc

    return PortableArtifactReport(
        sha256=actual_hash,
        entry_count=len(infos),
        source_sha=expected_git_sha,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--checksum-file", type=Path, required=True)
    parser.add_argument("--expected-git-sha", required=True)
    args = parser.parse_args()
    report = verify_portable_artifact(
        args.zip_path,
        args.checksum_file,
        expected_git_sha=args.expected_git_sha,
    )
    print(
        f"Portable ZIP VERIFIED: {report.entry_count} files; "
        f"SHA-256 {report.sha256}; source {report.source_sha}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
