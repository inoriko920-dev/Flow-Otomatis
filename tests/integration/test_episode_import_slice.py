from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from flow_otomatis.application.services import EpisodeImportService
from flow_otomatis.domain.errors import PackageSecurityError, PackageValidationError
from flow_otomatis.domain.scene import SceneReadiness
from flow_otomatis.infrastructure.filesystem import EpisodePackageReader
from flow_otomatis.infrastructure.persistence import SqliteWorkspaceRepository


def _manifest(*, first_target: float = 7.32) -> dict[str, object]:
    scenes: list[dict[str, object]] = [
        {
            "scene_id": "SCENE_016",
            "target_duration_s": first_target,
            "recommended_flow_duration_s": 10,
            "selected_flow_duration_s": None,
            "image_file": "../08_APPROVED_IMAGES/EP001__IMAGE__SCENE_016__v1.0.png",
            "motion_prompt": "Slow cinematic push-in with stable identity.",
            "model": "Omni Flash 1.1",
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "status": "READY_FOR_DURATION_SELECTION",
            "trim_target_s": first_target,
        },
        {
            "scene_id": "SCENE_017",
            "target_duration_s": 5.42,
            "recommended_flow_duration_s": 6,
            "selected_flow_duration_s": 6,
            "image_file": "../08_APPROVED_IMAGES/EP001__IMAGE__SCENE_017__v1.0.png",
            "motion_prompt": "Subtle parallax and a controlled camera move.",
            "model": "Omni Flash 1.1",
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "status": "READY",
            "trim_target_s": 5.42,
        },
    ]
    return {
        "schema_version": "1.0",
        "episode_id": "EP001_STEVE_JOBS",
        "project_name": "Steve Jobs Animated Biography",
        "production_profile": {
            "model": "Omni Flash 1.1",
            "resolution": "720p",
            "aspect_ratio": "16:9",
        },
        "scene_count": len(scenes),
        "scenes": scenes,
        "created_at": "2026-10-07T01:00:00+07:00",
        "source_versions": {
            "audio": "v1.0",
            "srt": "v1.0",
            "beat_map": "v1.0",
            "storyboard": "v1.0",
            "images": "v1.0",
        },
    }


def _write_package(path: Path, manifest: dict[str, object]) -> Path:
    root = "EP001_STEVE_JOBS_COMPLETE"
    manifest_name = f"{root}/09_FLOW_PROMPTS_AND_TAKES/FLOW_OTOMATIS_IMPORT.json"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(manifest_name, json.dumps(manifest))
        archive.writestr(
            f"{root}/08_APPROVED_IMAGES/EP001__IMAGE__SCENE_016__v1.0.png",
            b"synthetic-image-16",
        )
        archive.writestr(
            f"{root}/08_APPROVED_IMAGES/EP001__IMAGE__SCENE_017__v1.0.png",
            b"synthetic-image-17",
        )
    return path


def test_happy_path_validates_recomputes_and_persists_workspace(tmp_path: Path) -> None:
    package = _write_package(tmp_path / "episode.zip", _manifest())
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    service = EpisodeImportService(EpisodePackageReader(), repository)

    draft = service.validate(package)

    assert draft.episode_id == "EP001_STEVE_JOBS"
    assert len(draft.scenes) == 2
    assert draft.scenes[0].recommended_flow_duration_s == 8
    assert draft.scenes[0].readiness is SceneReadiness.NEEDS_DURATION_SELECTION
    assert draft.scenes[1].readiness is SceneReadiness.READY
    assert draft.blocking_count == 0

    persisted = service.create_workspace(draft)
    reloaded = repository.load("EP001_STEVE_JOBS")

    assert persisted == reloaded
    assert reloaded is not None
    assert reloaded.scenes[0].target_duration_s == 7.32
    assert (tmp_path / "projects" / "EP001_STEVE_JOBS" / "project.sqlite3").is_file()


def test_target_over_ten_seconds_is_rejected_before_persistence(tmp_path: Path) -> None:
    package = _write_package(
        tmp_path / "invalid-duration.zip",
        _manifest(first_target=10.01),
    )
    projects_root = tmp_path / "projects"
    service = EpisodeImportService(
        EpisodePackageReader(),
        SqliteWorkspaceRepository(projects_root),
    )

    with pytest.raises(PackageValidationError) as exc_info:
        service.import_package(package)

    assert exc_info.value.code == "MANIFEST_SCHEMA_INVALID"
    assert not projects_root.exists()


def test_zip_path_traversal_is_rejected(tmp_path: Path) -> None:
    package = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("../outside.txt", "unsafe")
        archive.writestr(
            "FLOW_OTOMATIS_IMPORT.json",
            json.dumps(_manifest()),
        )

    with pytest.raises(PackageSecurityError):
        EpisodePackageReader().load(package)
