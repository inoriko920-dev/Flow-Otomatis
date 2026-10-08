"""Safe local reader for Flow-Otomatis episode packages."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from pydantic import ValidationError

from flow_otomatis.application.ports.episode_package import (
    PackageSceneEvidence,
    PackageSnapshot,
)
from flow_otomatis.contracts.package import ImportManifest
from flow_otomatis.domain.errors import PackageSecurityError, PackageValidationError

_MANIFEST_NAME = "FLOW_OTOMATIS_IMPORT.json"


class EpisodePackageReader:
    """Read ZIP/directory/manifest JSON without unsafe extraction."""

    def load(self, source_path: Path) -> PackageSnapshot:
        source = source_path.expanduser().resolve()
        if source.is_file() and source.suffix.lower() == ".zip":
            return self._load_zip(source)
        if source.is_file() and source.suffix.lower() == ".json":
            return self._load_manifest_path(source)
        if source.is_dir():
            manifests = list(source.rglob(_MANIFEST_NAME))
            if len(manifests) != 1:
                raise PackageValidationError(
                    f"Expected exactly one {_MANIFEST_NAME}, found {len(manifests)}",
                    code="MANIFEST_COUNT_INVALID",
                )
            return self._load_manifest_path(manifests[0], package_root=source)
        raise PackageValidationError(
            "Episode package must be a ZIP, FLOW_OTOMATIS_IMPORT.json, or directory",
            code="PACKAGE_SOURCE_UNSUPPORTED",
        )

    def image_digest(self, source_path: Path, scene_id: str, image_file: str) -> str:
        """Hash an approved image using the package's ZIP or filesystem resolver."""

        snapshot = self.load(source_path)
        evidence = next(
            (item for item in snapshot.scenes if item.scene.scene_id == scene_id),
            None,
        )
        if evidence is None or evidence.scene.image_file != image_file or not evidence.image_exists:
            raise PackageValidationError(
                f"Scene {scene_id}: approved image is unavailable or changed",
                code="IMAGE_NOT_AVAILABLE",
            )

        source = source_path.expanduser().resolve()
        digest = hashlib.sha256()
        bytes_read = 0
        try:
            if source.suffix.lower() == ".zip":
                with zipfile.ZipFile(source) as archive:
                    names = [name for name in archive.namelist() if not name.endswith("/")]
                    self._validate_archive_names(names)
                    manifests = [
                        name for name in names if PurePosixPath(name).name == _MANIFEST_NAME
                    ]
                    if len(manifests) != 1:
                        raise PackageValidationError(
                            "ZIP manifest is missing or ambiguous",
                            code="MANIFEST_COUNT_INVALID",
                        )
                    member = self._resolve_member(manifests[0], image_file)
                    with archive.open(member) as stream:
                        while chunk := stream.read(1024 * 1024):
                            digest.update(chunk)
                            bytes_read += len(chunk)
            else:
                manifest_path = snapshot.source_path
                package_root = self._infer_directory_root(manifest_path)
                image_path = self._resolve_disk_ref(package_root, manifest_path.parent, image_file)
                if not image_path.is_file():
                    raise PackageValidationError(
                        f"Scene {scene_id}: source image file is missing",
                        code="IMAGE_NOT_AVAILABLE",
                    )
                with image_path.open("rb") as stream:
                    while chunk := stream.read(1024 * 1024):
                        digest.update(chunk)
                        bytes_read += len(chunk)
        except (OSError, zipfile.BadZipFile, RuntimeError, KeyError, ValueError) as exc:
            raise PackageValidationError(
                f"Scene {scene_id}: source image cannot be read",
                code="IMAGE_READ_FAILED",
            ) from exc
        if bytes_read == 0:
            raise PackageValidationError(
                f"Scene {scene_id}: source image is empty",
                code="IMAGE_EMPTY",
            )
        return digest.hexdigest()

    def _load_zip(self, source: Path) -> PackageSnapshot:
        try:
            with zipfile.ZipFile(source) as archive:
                names = [name for name in archive.namelist() if not name.endswith("/")]
                self._validate_archive_names(names)
                manifests = [name for name in names if PurePosixPath(name).name == _MANIFEST_NAME]
                if len(manifests) != 1:
                    raise PackageValidationError(
                        f"Expected exactly one {_MANIFEST_NAME}, found {len(manifests)}",
                        code="MANIFEST_COUNT_INVALID",
                    )
                manifest_name = manifests[0]
                manifest = self._parse_manifest(archive.read(manifest_name))
                name_set = set(names)
                evidence = tuple(
                    PackageSceneEvidence(
                        scene=scene,
                        image_exists=self._resolve_member(manifest_name, scene.image_file)
                        in name_set,
                        motion_prompt=self._resolve_zip_prompt(
                            archive,
                            name_set,
                            manifest_name,
                            scene.motion_prompt,
                            scene.scene_id,
                        ),
                    )
                    for scene in manifest.scenes
                )
                return PackageSnapshot(source, manifest, evidence)
        except zipfile.BadZipFile as exc:
            raise PackageValidationError(
                "Episode package ZIP is corrupt or unreadable",
                code="PACKAGE_ZIP_INVALID",
            ) from exc

    def _load_manifest_path(
        self,
        manifest_path: Path,
        *,
        package_root: Path | None = None,
    ) -> PackageSnapshot:
        manifest_file = manifest_path.resolve()
        if manifest_file.name != _MANIFEST_NAME:
            raise PackageValidationError(
                f"JSON file must be named {_MANIFEST_NAME}",
                code="MANIFEST_NAME_INVALID",
            )

        root = (
            package_root.resolve()
            if package_root is not None
            else self._infer_directory_root(manifest_file)
        )
        if not manifest_file.is_relative_to(root):
            raise PackageSecurityError("Manifest resolves outside the package root")

        try:
            manifest = self._parse_manifest(manifest_file.read_bytes())
        except OSError as exc:
            raise PackageValidationError(
                "Manifest could not be read",
                code="MANIFEST_READ_FAILED",
            ) from exc

        evidence: list[PackageSceneEvidence] = []
        for scene in manifest.scenes:
            image_path = self._resolve_disk_ref(root, manifest_file.parent, scene.image_file)
            prompt = self._resolve_disk_prompt(
                root,
                manifest_file.parent,
                scene.motion_prompt,
                scene.scene_id,
            )
            evidence.append(
                PackageSceneEvidence(
                    scene=scene,
                    image_exists=image_path.is_file(),
                    motion_prompt=prompt,
                )
            )
        return PackageSnapshot(manifest_file, manifest, tuple(evidence))

    def _parse_manifest(self, raw: bytes) -> ImportManifest:
        try:
            payload: Any = json.loads(raw.decode("utf-8-sig"))
            return ImportManifest.model_validate(payload)
        except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
            raise PackageValidationError(
                f"Invalid {_MANIFEST_NAME}: {exc}",
                code="MANIFEST_SCHEMA_INVALID",
            ) from exc

    def _validate_archive_names(self, names: list[str]) -> None:
        for raw_name in names:
            if "\x00" in raw_name:
                raise PackageSecurityError("Archive contains a NUL path")
            path = PurePosixPath(raw_name.replace("\\", "/"))
            if path.is_absolute() or ".." in path.parts:
                raise PackageSecurityError(f"Unsafe archive entry: {raw_name}")
            if path.parts and ":" in path.parts[0]:
                raise PackageSecurityError(f"Unsafe archive drive path: {raw_name}")

    def _resolve_member(self, manifest_name: str, reference: str) -> str:
        base_parts = list(PurePosixPath(manifest_name).parent.parts)
        return self._normalize_relative_parts(base_parts, reference)

    def _normalize_relative_parts(self, base_parts: list[str], reference: str) -> str:
        parts = list(base_parts)
        ref_path = PurePosixPath(reference.replace("\\", "/"))
        if ref_path.is_absolute():
            raise PackageSecurityError(f"Absolute package path is not allowed: {reference}")
        for part in ref_path.parts:
            if part in {"", "."}:
                continue
            if part == "..":
                if not parts:
                    raise PackageSecurityError(
                        f"Package reference escapes archive root: {reference}"
                    )
                parts.pop()
                continue
            if ":" in part:
                raise PackageSecurityError(f"Drive-like package path is not allowed: {reference}")
            parts.append(part)
        if not parts:
            raise PackageSecurityError(f"Package reference resolves to root: {reference}")
        return PurePosixPath(*parts).as_posix()

    def _resolve_zip_prompt(
        self,
        archive: zipfile.ZipFile,
        names: set[str],
        manifest_name: str,
        value: str,
        scene_id: str,
    ) -> str:
        stripped = value.strip()
        if not stripped:
            return ""
        if "\n" in stripped or "\r" in stripped:
            return stripped
        if not stripped.lower().endswith(".txt"):
            return stripped
        member = self._resolve_member(manifest_name, stripped)
        if member not in names:
            raise PackageValidationError(
                f"Scene {scene_id}: file prompt tidak ditemukan: {stripped}",
                code="PROMPT_FILE_MISSING",
            )
        try:
            return archive.read(member).decode("utf-8-sig").strip()
        except UnicodeDecodeError as exc:
            raise PackageValidationError(
                f"Motion prompt file is not UTF-8 text: {member}",
                code="PROMPT_READ_FAILED",
            ) from exc

    def _infer_directory_root(self, manifest_file: Path) -> Path:
        parent = manifest_file.parent
        if parent.name == "09_FLOW_PROMPTS_AND_TAKES":
            return parent.parent
        return parent

    def _resolve_disk_ref(self, root: Path, base: Path, reference: str) -> Path:
        candidate = (base / reference).resolve()
        if not candidate.is_relative_to(root):
            raise PackageSecurityError(f"Package reference escapes root: {reference}")
        return candidate

    def _resolve_disk_prompt(
        self,
        root: Path,
        base: Path,
        value: str,
        scene_id: str,
    ) -> str:
        stripped = value.strip()
        if not stripped or "\n" in stripped or "\r" in stripped:
            return stripped
        if not stripped.lower().endswith(".txt"):
            return stripped
        candidate = self._resolve_disk_ref(root, base, stripped)
        if not candidate.is_file():
            raise PackageValidationError(
                f"Scene {scene_id}: file prompt tidak ditemukan: {stripped}",
                code="PROMPT_FILE_MISSING",
            )
        try:
            return candidate.read_text(encoding="utf-8-sig").strip()
        except (OSError, UnicodeDecodeError) as exc:
            raise PackageValidationError(
                f"Motion prompt file could not be read: {candidate.name}",
                code="PROMPT_READ_FAILED",
            ) from exc
