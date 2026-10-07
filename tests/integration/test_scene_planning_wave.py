from __future__ import annotations

import json
from pathlib import Path

import pytest

from flow_otomatis.application.services import EpisodeImportService, ScenePlanningService
from flow_otomatis.domain.errors import InvalidDurationError
from flow_otomatis.domain.scene import SceneReadiness
from flow_otomatis.infrastructure.filesystem import EpisodePackageReader
from flow_otomatis.infrastructure.persistence import SqliteWorkspaceRepository


def _write_directory_package(root: Path, *, include_image: bool = True) -> Path:
    prompt_dir = root / "09_FLOW_PROMPTS_AND_TAKES"
    image_dir = root / "08_APPROVED_IMAGES"
    prompt_dir.mkdir(parents=True)
    image_dir.mkdir(parents=True)

    image_name = "EP011__IMAGE__SCENE_016__v1.0.png"
    manifest = {
        "schema_version": "1.0",
        "episode_id": "EP011_SCENE_PLANNING",
        "project_name": "Scene Planning Test",
        "production_profile": {
            "model": "Omni Flash 1.1",
            "resolution": "720p",
            "aspect_ratio": "16:9",
        },
        "scene_count": 1,
        "scenes": [
            {
                "scene_id": "SCENE_016",
                "target_duration_s": 7.32,
                "recommended_flow_duration_s": 8,
                "selected_flow_duration_s": None,
                "image_file": f"../08_APPROVED_IMAGES/{image_name}",
                "motion_prompt": "Slow cinematic push-in.",
                "model": "Omni Flash 1.1",
                "resolution": "720p",
                "aspect_ratio": "16:9",
                "status": "READY_FOR_DURATION_SELECTION",
                "trim_target_s": 7.32,
            }
        ],
        "created_at": "2026-10-07T01:00:00+07:00",
        "source_versions": {"images": "v1.0"},
    }
    (prompt_dir / "FLOW_OTOMATIS_IMPORT.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    if include_image:
        (image_dir / image_name).write_bytes(b"synthetic-image")
    return root


def _services(tmp_path: Path) -> tuple[EpisodeImportService, ScenePlanningService]:
    reader = EpisodePackageReader()
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    return (
        EpisodeImportService(reader, repository),
        ScenePlanningService(reader, repository),
    )


def test_duration_selection_persists_and_target_stays_immutable(tmp_path: Path) -> None:
    package = _write_directory_package(tmp_path / "episode")
    importer, planner = _services(tmp_path)
    workspace = importer.import_package(package)
    original_target = workspace.scenes[0].target_duration_s

    updated = planner.select_flow_duration(
        workspace.episode_id,
        "SCENE_016",
        8,
    )
    reloaded = planner.load_workspace(workspace.episode_id)

    assert updated == reloaded
    assert reloaded.scenes[0].selected_flow_duration_s == 8
    assert reloaded.scenes[0].readiness is SceneReadiness.READY
    assert reloaded.scenes[0].target_duration_s == original_target


def test_shorter_duration_is_blocked_without_mutating_persisted_state(tmp_path: Path) -> None:
    package = _write_directory_package(tmp_path / "episode")
    importer, planner = _services(tmp_path)
    workspace = importer.import_package(package)

    with pytest.raises(InvalidDurationError):
        planner.select_flow_duration(workspace.episode_id, "SCENE_016", 6)

    reloaded = planner.load_workspace(workspace.episode_id)
    assert reloaded.scenes[0].selected_flow_duration_s is None
    assert reloaded.scenes[0].target_duration_s == 7.32


def test_image_rescan_recomputes_readiness_deterministically(tmp_path: Path) -> None:
    package = _write_directory_package(tmp_path / "episode", include_image=False)
    importer, planner = _services(tmp_path)
    workspace = importer.import_package(package)

    assert workspace.scenes[0].readiness is SceneReadiness.MISSING_IMAGE

    image = package / "08_APPROVED_IMAGES" / "EP011__IMAGE__SCENE_016__v1.0.png"
    image.write_bytes(b"now-present")
    rescanned = planner.rescan_images(workspace.episode_id)
    assert rescanned.scenes[0].readiness is SceneReadiness.NEEDS_DURATION_SELECTION

    planner.select_flow_duration(workspace.episode_id, "SCENE_016", 8)
    image.unlink()
    rescanned_again = planner.rescan_images(workspace.episode_id)
    assert rescanned_again.scenes[0].selected_flow_duration_s == 8
    assert rescanned_again.scenes[0].readiness is SceneReadiness.MISSING_IMAGE
