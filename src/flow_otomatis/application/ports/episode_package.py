"""Application-owned port for reading an episode package."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from flow_otomatis.contracts.package import ImportManifest, ImportScene


@dataclass(frozen=True, slots=True)
class PackageSceneEvidence:
    """Filesystem evidence paired with one manifest scene."""

    scene: ImportScene
    image_exists: bool
    motion_prompt: str


@dataclass(frozen=True, slots=True)
class PackageSnapshot:
    """Validated manifest plus safe local package evidence."""

    source_path: Path
    manifest: ImportManifest
    scenes: tuple[PackageSceneEvidence, ...]


class EpisodePackagePort(Protocol):
    """Read and validate local package structure behind an application boundary."""

    def load(self, source_path: Path) -> PackageSnapshot:
        """Load one ZIP or manifest JSON without extracting unsafe archive content."""
        ...


class EpisodeImageVerifierPort(Protocol):
    """Read original approved image bytes through the canonical package boundary."""

    def image_digest(self, source_path: Path, scene_id: str, image_file: str) -> str:
        """Return SHA-256 of a nonempty source image, or fail closed."""
        ...
