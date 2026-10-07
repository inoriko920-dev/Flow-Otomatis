from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from flow_otomatis.application.services import EpisodeImportService, ScenePlanningService
from flow_otomatis.infrastructure.filesystem import EpisodePackageReader
from flow_otomatis.infrastructure.persistence import SqliteWorkspaceRepository
from flow_otomatis.presentation.main_window import MainWindow


def _package(root: Path) -> Path:
    prompt_dir = root / "09_FLOW_PROMPTS_AND_TAKES"
    image_dir = root / "08_APPROVED_IMAGES"
    prompt_dir.mkdir(parents=True)
    image_dir.mkdir(parents=True)
    image_name = "EP012__IMAGE__SCENE_016__v1.0.png"
    (image_dir / image_name).write_bytes(b"image")
    manifest = {
        "schema_version": "1.0",
        "episode_id": "EP012_UI_PLANNING",
        "project_name": "UI Planning Test",
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
                "motion_prompt": "Stable push-in.",
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
    return root


def test_scene_inspector_duration_buttons_call_real_planning_service(tmp_path: Path, qtbot) -> None:
    reader = EpisodePackageReader()
    repository = SqliteWorkspaceRepository(tmp_path / "projects")
    importer = EpisodeImportService(reader, repository)
    planner = ScenePlanningService(reader, repository)
    package = _package(tmp_path / "episode")
    workspace = importer.import_package(package)

    window = MainWindow(
        episode_import_service=importer,
        scene_planning_service=planner,
    )
    qtbot.addWidget(window)
    window.show_workspace_state(workspace)

    buttons = {button.text(): button for button in window.findChildren(QPushButton)}
    assert buttons["4s"].isEnabled() is False
    assert buttons["6s"].isEnabled() is False
    assert buttons["8s"].isEnabled() is True
    assert buttons["10s"].isEnabled() is True

    qtbot.mouseClick(buttons["8s"], Qt.MouseButton.LeftButton)

    assert window.current_workspace is not None
    assert window.current_workspace.scenes[0].selected_flow_duration_s == 8
    assert planner.load_workspace("EP012_UI_PLANNING").scenes[0].selected_flow_duration_s == 8
