"""Offline Scene preflight must remain independent of provider and durable queue."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime

from PySide6.QtWidgets import QPushButton, QTableWidget

from flow_otomatis.application.services.local_scene_preflight import (
    prepare_local_scene_preflight,
)
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.presentation.local_scene_preflight_view import LocalScenePreflightDialog


def _scene(
    scene_id: str,
    *,
    image: bool = True,
    prompt: str = "Secret full motion prompt that must never be exported",
    target: float = 7.32,
    flow: int | None = 8,
    readiness: SceneReadiness = SceneReadiness.READY,
) -> WorkspaceScene:
    return WorkspaceScene(
        scene_id=scene_id,
        image_file=f"C:/private/source/{scene_id}.png",
        image_exists=image,
        motion_prompt=prompt,
        target_duration_s=target,
        recommended_flow_duration_s=8,
        selected_flow_duration_s=flow,
        readiness=readiness,
        trim_target_s=7.32,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
    )


def _workspace(*scenes: WorkspaceScene) -> WorkspaceState:
    now = datetime(2026, 10, 9, tzinfo=UTC)
    return WorkspaceState(
        schema_version="1.0",
        episode_id="EP_LOCAL_QUEUE",
        project_name="Offline Gate",
        source_package_path="C:/private/source/personal_package.zip",
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=tuple(scenes),
    )


def test_preflight_only_includes_verified_local_inputs_and_no_private_paths() -> None:
    workspace = _workspace(
        _scene("SCENE_001"),
        _scene(
            "SCENE_002",
            image=False,
            readiness=SceneReadiness.MISSING_IMAGE,
        ),
        _scene(
            "SCENE_003",
            flow=None,
            readiness=SceneReadiness.NEEDS_DURATION_SELECTION,
        ),
    )
    original = repr(workspace)
    report = prepare_local_scene_preflight(workspace)
    assert report["mode"] == "NON_EXECUTABLE_LOCAL_SCENE_PREFLIGHT"
    assert report["ready_count"] == 1
    assert report["held_count"] == 2
    assert [row["scene_id"] for row in report["ready"]] == ["SCENE_001"]
    assert [row["scene_id"] for row in report["held"]] == ["SCENE_002", "SCENE_003"]
    assert report["ready"][0]["flow_duration_s"] == 8
    assert "GAMBAR HILANG" in report["held"][0]["issues"]
    assert "PILIH DURASI" in report["held"][1]["issues"]
    assert report["live_dispatch_allowed"] is False
    assert report["durable_jobs_created"] is False
    assert report["image_bytes_verified"] is False
    serialized = json.dumps(report, ensure_ascii=False, allow_nan=False)
    assert "Secret full motion prompt" not in serialized
    assert "C:/private" not in serialized
    assert "personal_package.zip" not in serialized
    assert repr(workspace) == original


def test_preflight_rejects_duplicate_stale_duration_and_nonfinite_target() -> None:
    stale = _scene("SCENE_STALE", image=False)
    repeated = _scene("SCENE_DUP")
    workspace = _workspace(
        repeated,
        repeated,
        stale,
        _scene("SCENE_BAD", target=float("nan")),
        _scene("SCENE_TOO_SHORT", target=8.2, flow=8),
        _scene("SCENE_INVALID", flow=5),
    )
    report = prepare_local_scene_preflight(workspace)
    assert report["ready_count"] == 0
    assert report["held_count"] == 6
    assert all(row["status"] == "DITAHAN" for row in report["held"])
    assert all("ID SCENE GANDA" in row["issues"] for row in report["held"][:2])
    assert "STATUS LOKAL TIDAK SESUAI" in report["held"][2]["issues"]
    assert report["held"][3]["target_duration_s"] is None
    assert "TARGET INVALID" in report["held"][3]["issues"]
    assert "DURASI INVALID" in report["held"][4]["issues"]
    assert "DURASI INVALID" in report["held"][5]["issues"]
    json.dumps(report, allow_nan=False)


def test_preflight_empty_workspace_is_held_not_a_ready_claim() -> None:
    report = prepare_local_scene_preflight(_workspace())
    assert report["total_scenes"] == 0
    assert report["ready_count"] == 0
    assert report["held_count"] == 0
    assert report["ready"] == []
    assert report["live_dispatch_allowed"] is False


def test_qt_preflight_dialog_displays_report_and_preserves_workspace(qtbot) -> None:
    workspace = _workspace(
        _scene("SCENE_001"),
        _scene("SCENE_002", prompt="", readiness=SceneReadiness.MISSING_PROMPT),
    )
    original = repr(workspace)
    dialog = LocalScenePreflightDialog(workspace)
    qtbot.addWidget(dialog)
    table = dialog.findChild(QTableWidget, "LocalPreflightTable")
    assert table is not None
    assert table.rowCount() == 2
    assert table.item(0, 3).text() == "SIAP INPUT LOKAL"
    assert table.item(1, 3).text() == "DITAHAN"
    assert "PROMPT HILANG" in table.item(1, 4).text()
    assert dialog.findChild(QPushButton, "LocalPreflightExport").isEnabled()
    assert "Bukan antrean" in dialog.report["warning"]
    assert repr(workspace) == original
    dialog.close()


def test_preflight_keeps_all_scene_ids_safe_if_input_id_is_malformed() -> None:
    workspace = _workspace(replace(_scene("SCENE_001"), scene_id="C:/private/key"))
    report = prepare_local_scene_preflight(workspace)
    assert report["ready_count"] == 0
    assert report["held"][0]["scene_id"] == "INVALID_SCENE_ID_AT_1"
    assert "C:/private/key" not in json.dumps(report)
