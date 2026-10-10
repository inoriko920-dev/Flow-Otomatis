from __future__ import annotations

import json
import zipfile
from pathlib import Path

from PySide6.QtWidgets import QLabel, QTableWidget

from flow_otomatis.application.services import EpisodeImportService
from flow_otomatis.application.services.local_scene_preflight import (
    prepare_local_scene_preflight,
)
from flow_otomatis.infrastructure.filesystem import EpisodePackageReader
from flow_otomatis.infrastructure.persistence import SqliteWorkspaceRepository
from flow_otomatis.presentation.main_window import MainWindow


def _package(path: Path) -> Path:
    root = "EP010_TEST_COMPLETE"
    manifest = {
        "schema_version": "1.0",
        "episode_id": "EP010_TEST",
        "project_name": "Real Workspace Test",
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
                "image_file": "../08_APPROVED_IMAGES/EP010__IMAGE__SCENE_016__v1.0.png",
                "motion_prompt": "Real prompt loaded from package.",
                "model": "Omni Flash 1.1",
                "resolution": "720p",
                "aspect_ratio": "16:9",
                "status": "READY_FOR_DURATION_SELECTION",
                "trim_target_s": 7.32,
            }
        ],
        "created_at": "2026-10-07T01:00:00+07:00",
        "source_versions": {"audio": "v1.0"},
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            f"{root}/09_FLOW_PROMPTS_AND_TAKES/FLOW_OTOMATIS_IMPORT.json",
            json.dumps(manifest),
        )
        archive.writestr(
            f"{root}/08_APPROVED_IMAGES/EP010__IMAGE__SCENE_016__v1.0.png",
            b"synthetic-image",
        )
    return path


def _visible_text(window: MainWindow) -> str:
    parts = [label.text() for label in window.findChildren(QLabel)]
    for table in window.findChildren(QTableWidget):
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None:
                    parts.append(item.text())
    return "\n".join(parts)


def test_real_package_validation_and_workspace_render_without_redesign(
    tmp_path: Path,
    qtbot: object,
) -> None:
    del qtbot
    service = EpisodeImportService(
        EpisodePackageReader(),
        SqliteWorkspaceRepository(tmp_path / "projects"),
    )
    window = MainWindow(episode_import_service=service)
    package = _package(tmp_path / "episode.zip")

    try:
        draft = window.import_episode_package(package)
        validation_text = _visible_text(window)

        assert window.fixture_code == "REAL_VALIDATION"
        assert draft.episode_id == "EP010_TEST"
        assert "Real Workspace Test" in validation_text
        assert "S016" in validation_text
        assert "7.32s" in validation_text
        assert "Belum dipilih" in validation_text

        persisted = window.create_pending_workspace()
        workspace_text = _visible_text(window)

        assert window.fixture_code == "REAL_WORKSPACE"
        assert window.current_workspace == persisted
        assert "Real prompt loaded from package." in workspace_text
        assert "8s • rekom." in workspace_text
        assert "Pilih Durasi" in workspace_text
        assert (tmp_path / "projects" / "EP010_TEST" / "project.sqlite3").is_file()
    finally:
        window.close()


def test_canonical_zip_reader_verifies_original_image_bytes_and_blocks_missing_source(
    tmp_path: Path,
) -> None:
    reader = EpisodePackageReader()
    repo = SqliteWorkspaceRepository(tmp_path / "projects_for_image_check")
    package = _package(tmp_path / "package_for_digest.zip")
    workspace = EpisodeImportService(reader, repo).import_package(package)

    verified = prepare_local_scene_preflight(workspace, image_verifier=reader)
    assert verified["image_integrity_check"] == "LOCAL_SOURCE_BYTES_READ"
    assert verified["verified_image_count"] == 1
    assert verified["unreadable_image_count"] == 0
    assert verified["image_bytes_verified"] is True
    assert verified["held"][0]["image_evidence"] == "BYTE TERBACA"

    package.unlink()
    missing = prepare_local_scene_preflight(workspace, image_verifier=reader)
    assert missing["verified_image_count"] == 0
    assert missing["unreadable_image_count"] == 1
    assert missing["image_bytes_verified"] is False
    assert "BYTE GAMBAR TIDAK TERBACA" in missing["held"][0]["issues"]
    assert str(tmp_path) not in json.dumps(missing)
    assert missing["live_dispatch_allowed"] is False
