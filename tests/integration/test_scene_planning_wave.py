from __future__ import annotations

import json
from dataclasses import replace
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

def test_fill_missing_recommended_durations_for_large_real_workspace_is_atomic(
    tmp_path: Path,
) -> None:
    package = _write_directory_package(tmp_path / "episode")
    importer, planner = _services(tmp_path)
    original = importer.import_package(package)
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    prototype = original.scenes[0]
    scenes = tuple(
        replace(
            prototype,
            scene_id=f"SCENE_{index:03d}",
            target_duration_s=(3.8, 5.42, 7.32, 9.1)[index % 4],
            trim_target_s=(3.8, 5.42, 7.32, 9.1)[index % 4],
            selected_flow_duration_s=10 if index == 0 else None,
            readiness=(
                SceneReadiness.NEEDS_DURATION_SELECTION
                if index != 0 else SceneReadiness.READY
            ),
            image_sha256_imported=f"{index:064x}",
        )
        for index in range(100)
    )
    repository.update(replace(original, scenes=scenes))
    plan = planner.preview_missing_recommended_durations(original.episode_id)
    assert len(plan) == 99
    assert dict(plan)["SCENE_001"] == 6
    assert dict(plan)["SCENE_002"] == 8
    assert dict(plan)["SCENE_003"] == 10
    before = repository.load(original.episode_id)
    assert before is not None
    assert before.scenes[1].selected_flow_duration_s is None

    after = planner.fill_missing_recommended_durations(original.episode_id)
    assert len(after.scenes) == 100
    assert after.ready_count == 100
    assert after.scenes[0].selected_flow_duration_s == 10
    assert [after.scenes[i].selected_flow_duration_s for i in range(1, 5)] == [
        6, 8, 10, 4
    ]
    assert after.scenes[67].image_sha256_imported == scenes[67].image_sha256_imported
    assert after.scenes[67].target_duration_s == scenes[67].target_duration_s
    assert after.scenes[67].trim_target_s == scenes[67].trim_target_s
    assert planner.preview_missing_recommended_durations(original.episode_id) == ()
    assert planner.fill_missing_recommended_durations(original.episode_id) == after


def test_auto_duration_planner_skips_invalid_targets_and_preserves_missing_inputs(
    tmp_path: Path,
) -> None:
    package = _write_directory_package(tmp_path / "episode")
    importer, planner = _services(tmp_path)
    original = importer.import_package(package)
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    base = original.scenes[0]
    scenes = (
        replace(base, scene_id="SCENE_IMAGE", image_exists=False),
        replace(
            base,
            scene_id="SCENE_PROMPT",
            motion_prompt="",
            image_sha256_imported="b" * 64,
        ),
        replace(base, scene_id="SCENE_INVALID", target_duration_s=11.0),
    )
    repository.update(replace(original, scenes=scenes))
    plan = planner.preview_missing_recommended_durations(original.episode_id)
    assert plan == (("SCENE_IMAGE", 8), ("SCENE_PROMPT", 8))
    result = planner.fill_missing_recommended_durations(original.episode_id)
    assert result.scenes[0].readiness is SceneReadiness.MISSING_IMAGE
    assert result.scenes[1].readiness is SceneReadiness.MISSING_PROMPT
    assert result.scenes[1].image_sha256_imported == "b" * 64
    assert result.scenes[2].selected_flow_duration_s is None
    assert result.scenes[2].target_duration_s == 11.0
