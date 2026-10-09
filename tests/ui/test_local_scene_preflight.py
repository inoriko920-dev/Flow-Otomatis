"""Offline Scene preflight must remain independent of provider and durable queue."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtWidgets import QComboBox, QFileDialog, QPushButton, QTableWidget

from flow_otomatis.application.services.local_scene_preflight import (
    prepare_local_scene_preflight,
)
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.presentation.credit_uix_preview import CreditUixDialog
from flow_otomatis.presentation.local_scene_preflight_view import LocalScenePreflightDialog
from flow_otomatis.presentation.main_window import MainWindow


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


def test_ui_preflight_is_local_only_and_recomputes_readonly(qtbot, monkeypatch) -> None:
    workspace = _workspace(_scene("SCENE_001"))
    dialog = CreditUixDialog(workspace=workspace, initial_state="UIX-01-A")
    qtbot.addWidget(dialog)
    button = dialog.findChild(QPushButton, "UixLocalPreflight")
    source = dialog.findChild(QComboBox, "UixDataSourceSelector")
    assert button is not None
    assert button.isEnabled() and not button.isHidden()

    inspections: list[dict[str, object]] = []

    def inspect(preview: LocalScenePreflightDialog) -> int:
        inspections.append(preview.report.copy())
        return 0

    monkeypatch.setattr(LocalScenePreflightDialog, "exec", inspect)
    button.click()
    assert len(inspections) == 1
    assert inspections[0]["ready_count"] == 1
    assert inspections[0]["durable_jobs_created"] is False

    source.setCurrentIndex(source.findData("demo"))
    assert button.isHidden() and not button.isEnabled()
    dialog.show_local_preflight()
    assert len(inspections) == 1
    source.setCurrentIndex(source.findData("local"))
    assert button.isEnabled()
    assert not dialog.live_dispatch_enabled
    dialog.close()


def test_preflight_export_is_create_only_and_never_overwrites(qtbot, monkeypatch, tmp_path) -> None:
    dialog = LocalScenePreflightDialog(_workspace(_scene("SCENE_001")))
    qtbot.addWidget(dialog)
    path = tmp_path / "preflight.json"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(path), "JSON (*.json)"),
    )
    dialog.export_json()
    original = path.read_bytes()
    assert json.loads(original)["live_dispatch_allowed"] is False

    from PySide6.QtWidgets import QMessageBox

    warnings: list[str] = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda _parent, _title, message: warnings.append(message),
    )
    dialog.export_json()
    assert warnings
    assert path.read_bytes() == original
    dialog.close()


def test_preflight_opens_held_scene_from_main_workspace_without_mutation(
    qtbot, monkeypatch
) -> None:
    workspace = _workspace(
        _scene("SCENE_001"),
        _scene(
            "SCENE_002",
            image=False,
            readiness=SceneReadiness.MISSING_IMAGE,
        ),
    )
    original = repr(workspace)
    window = MainWindow()
    qtbot.addWidget(window)
    window.show_workspace_state(workspace)
    button = window.findChild(QPushButton, "LocalPreflightWorkspaceAction")
    assert button is not None
    assert button.isEnabled()

    def choose_scene(dialog: LocalScenePreflightDialog) -> int:
        assert dialog.report["ready_count"] == 1
        assert dialog.report["held_count"] == 1
        table = dialog.findChild(QTableWidget, "LocalPreflightTable")
        table.setCurrentCell(1, 0)
        open_button = dialog.findChild(QPushButton, "LocalPreflightOpenScene")
        assert open_button.isEnabled()
        open_button.click()
        return int(dialog.result())

    monkeypatch.setattr(LocalScenePreflightDialog, "exec", choose_scene)
    button.click()
    assert window.fixture_code == "REAL_WORKSPACE"
    assert window._selected_scene_id == "SCENE_002"
    table = next(
        view
        for view in window.findChildren(QTableWidget)
        if view.columnCount() == 9 and view.rowCount() == 2
    )
    assert table.item(table.currentRow(), 0).text() == "S002"
    assert window.current_workspace is workspace
    assert repr(workspace) == original
    window.close()


def test_preflight_navigation_rejects_duplicate_ids_and_stale_context(qtbot, monkeypatch) -> None:
    duplicate = _workspace(_scene("SCENE_001"), _scene("SCENE_001"))
    dialog = LocalScenePreflightDialog(duplicate)
    qtbot.addWidget(dialog)
    table = dialog.findChild(QTableWidget, "LocalPreflightTable")
    open_button = dialog.findChild(QPushButton, "LocalPreflightOpenScene")
    for row in range(2):
        table.setCurrentCell(row, 0)
        assert not open_button.isEnabled()
    dialog._request_open_scene()
    assert dialog.requested_scene_id is None
    dialog.close()

    workspace = _workspace(_scene("SCENE_001"), _scene("SCENE_002"))
    window = MainWindow()
    qtbot.addWidget(window)
    window.show_workspace_state(workspace)
    original = window._selected_scene_id

    def change_workspace_during_preflight(view: LocalScenePreflightDialog) -> int:
        view.table.setCurrentCell(1, 0)
        view._request_open_scene()
        window.show_workspace_state(duplicate)
        return int(view.result())

    monkeypatch.setattr(LocalScenePreflightDialog, "exec", change_workspace_during_preflight)
    window.open_local_scene_preflight()
    assert window.current_workspace is duplicate
    assert window._selected_scene_id != "SCENE_002"
    assert original == "SCENE_001"
    window.close()


def test_preflight_cancel_and_empty_workspace_have_no_navigation(qtbot, monkeypatch) -> None:
    dialog = LocalScenePreflightDialog(_workspace())
    qtbot.addWidget(dialog)
    assert dialog.table.rowCount() == 0
    assert not dialog.open_scene_button.isEnabled()
    assert dialog.requested_scene_id is None
    dialog.close()

    workspace = _workspace(_scene("SCENE_001"), _scene("SCENE_002"))
    window = MainWindow()
    qtbot.addWidget(window)
    window.show_workspace_state(workspace)
    monkeypatch.setattr(LocalScenePreflightDialog, "exec", lambda _dialog: 0)
    window.open_local_scene_preflight()
    assert window._selected_scene_id == "SCENE_001"
    assert window.current_workspace is workspace
    window.close()


def test_preflight_nested_ui_dialog_can_return_selected_scene(qtbot, monkeypatch) -> None:
    workspace = _workspace(_scene("SCENE_001"), _scene("SCENE_002"))
    preview = CreditUixDialog(workspace=workspace)
    qtbot.addWidget(preview)

    def select_second(dialog: LocalScenePreflightDialog) -> int:
        dialog.table.setCurrentCell(1, 0)
        dialog.open_scene_button.click()
        return int(dialog.result())

    monkeypatch.setattr(LocalScenePreflightDialog, "exec", select_second)
    preview.show_local_preflight()
    assert preview.requested_scene_id == "SCENE_002"
    assert preview.result() == preview.DialogCode.Accepted
    assert not preview.live_dispatch_enabled


class _LocalImageReader:
    """An in-memory spy: no provider, database, sessions, or network."""

    def __init__(self, missing: tuple[str, ...] = ()) -> None:
        self.missing = missing
        self.calls: list[tuple[Path, str, str]] = []

    def image_digest(self, source_path: Path, scene_id: str, image_file: str) -> str:
        self.calls.append((source_path, scene_id, image_file))
        if scene_id in self.missing:
            raise OSError("C:/private/source/secret_image_not_found.png")
        return "a" * 64


def test_source_image_scan_blocks_unreadable_bytes_and_preserves_privacy() -> None:
    verifier = _LocalImageReader(("SCENE_002",))
    workspace = _workspace(_scene("SCENE_001"), _scene("SCENE_002"))
    baseline = prepare_local_scene_preflight(workspace)
    assert baseline["ready_count"] == 2
    assert baseline["image_integrity_check"] == "NOT_RUN"

    report = prepare_local_scene_preflight(workspace, image_verifier=verifier)
    assert report["image_integrity_check"] == "LOCAL_SOURCE_BYTES_READ"
    assert report["ready_count"] == 1
    assert report["held_count"] == 1
    assert report["verified_image_count"] == 1
    assert report["unreadable_image_count"] == 1
    assert report["image_bytes_verified"] is False
    assert report["ready"][0]["image_evidence"] == "BYTE TERBACA"
    assert report["held"][0]["image_evidence"] == "TIDAK TERBACA"
    assert "BYTE GAMBAR TIDAK TERBACA" in report["held"][0]["issues"]
    assert len(verifier.calls) == 2
    assert "C:/private" not in json.dumps(report)
    assert "Secret full motion prompt" not in json.dumps(report)


def test_local_scan_fail_closed_for_invalid_digests_and_ambiguous_scene_ids() -> None:
    class InvalidReader(_LocalImageReader):
        def image_digest(self, source_path: Path, scene_id: str, image_file: str) -> str:
            super().image_digest(source_path, scene_id, image_file)
            return "bad-digest"

    verifier = InvalidReader()
    report = prepare_local_scene_preflight(_workspace(_scene("SCENE_001")), image_verifier=verifier)
    assert report["ready_count"] == 0
    assert report["unreadable_image_count"] == 1
    assert report["live_dispatch_allowed"] is False

    reader = _LocalImageReader()
    report = prepare_local_scene_preflight(
        _workspace(_scene("SCENE_DUP"), _scene("SCENE_DUP")),
        image_verifier=reader,
    )
    assert report["ready_count"] == 0
    assert report["unreadable_image_count"] == 2
    assert reader.calls == []
    assert all("ID SCENE GANDA" in row["issues"] for row in report["held"])


def test_async_qt_image_scan_refreshes_report_without_creating_jobs(qtbot) -> None:
    workspace = _workspace(_scene("SCENE_001"), _scene("SCENE_002"))
    original = repr(workspace)
    verifier = _LocalImageReader(("SCENE_002",))
    dialog = LocalScenePreflightDialog(workspace, image_verifier=verifier)
    qtbot.addWidget(dialog)
    assert dialog.report["image_integrity_check"] == "NOT_RUN"
    assert dialog.verify_button.isEnabled()
    dialog.verify_button.click()
    qtbot.waitUntil(
        lambda: dialog.report["image_integrity_check"] == "LOCAL_SOURCE_BYTES_READ",
        timeout=15000,
    )
    assert dialog.verify_button.isEnabled()
    assert dialog.export_button.isEnabled()
    assert dialog.report["held_count"] == 1
    assert dialog.table.item(1, 5).text() == "TIDAK TERBACA"
    assert "tidak terbaca: 1" in dialog.image_check_status.text()
    assert dialog.report["durable_jobs_created"] is False
    assert repr(workspace) == original
    dialog.close()


def test_image_byte_verification_is_unavailable_until_verifier_is_injected(qtbot) -> None:
    dialog = LocalScenePreflightDialog(_workspace(_scene("SCENE_001")))
    qtbot.addWidget(dialog)
    assert not dialog.verify_button.isEnabled()
    dialog.verify_source_images()
    assert dialog.report["image_integrity_check"] == "NOT_RUN"
    assert dialog.report["image_bytes_verified"] is False
    dialog.close()


def test_partial_missing_scene_is_not_claimed_as_all_image_bytes_verified() -> None:
    workspace = _workspace(
        _scene("SCENE_001"),
        _scene(
            "SCENE_002", image=False, readiness=SceneReadiness.MISSING_IMAGE
        ),
    )
    reader = _LocalImageReader()
    report = prepare_local_scene_preflight(workspace, image_verifier=reader)
    assert report["verified_image_count"] == 1
    assert report["unreadable_image_count"] == 0
    assert report["image_bytes_verified"] is False
    assert report["image_baselines_verified"] is False
    assert report["ready_count"] == 1
    assert report["held_count"] == 1
    assert report["held"][0]["image_evidence"] == "GAMBAR HILANG"
    assert [call[1] for call in reader.calls] == ["SCENE_001"]

    only_missing = prepare_local_scene_preflight(
        _workspace(
            _scene("SCENE_003", image=False, readiness=SceneReadiness.MISSING_IMAGE)
        ),
        image_verifier=reader,
    )
    assert only_missing["verified_image_count"] == 0
    assert only_missing["image_bytes_verified"] is False
    assert only_missing["held_count"] == 1
