"""Bind real STEP 10 workspace state to the frozen STEP 09 presentation."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness
from flow_otomatis.presentation.fixtures import get_fixture
from flow_otomatis.presentation.screen_factory import build_right_panel, build_screen


def _display_scene_id(scene_id: str) -> str:
    return scene_id.replace("SCENE_", "S", 1)


def _status_text(readiness: SceneReadiness) -> str:
    return {
        SceneReadiness.READY: "Siap",
        SceneReadiness.NEEDS_DURATION_SELECTION: "Pilih Durasi",
        SceneReadiness.MISSING_IMAGE: "Gambar Hilang",
        SceneReadiness.MISSING_PROMPT: "Prompt Hilang",
        SceneReadiness.INVALID_DURATION: "Durasi Invalid",
    }[readiness]


def _table_with_columns(root: QWidget, count: int) -> QTableWidget:
    for table in root.findChildren(QTableWidget):
        if table.columnCount() == count:
            return table
    raise RuntimeError(f"Frozen view is missing a {count}-column table")


def _button(root: QWidget, text: str) -> QPushButton:
    for button in root.findChildren(QPushButton):
        if button.text() == text:
            return button
    raise RuntimeError(f"Frozen view is missing button: {text}")


def _set_cell(table: QTableWidget, row: int, column: int, text: str) -> None:
    table.setItem(row, column, QTableWidgetItem(text))


def build_validation_view(
    workspace: WorkspaceState,
    *,
    on_create: Callable[[], object],
    on_cancel: Callable[[], object],
) -> QWidget:
    """Render real manifest validation inside the frozen validation composition."""

    root = build_screen(get_fixture("UI-IMG-012B"))
    table = _table_with_columns(root, 7)
    table.setRowCount(len(workspace.scenes))

    for row, scene in enumerate(workspace.scenes):
        values = (
            _display_scene_id(scene.scene_id),
            "Approved" if scene.image_exists else "Missing",
            "Ada" if scene.motion_prompt.strip() else "Missing",
            f"{scene.target_duration_s:.2f}s",
            f"{scene.recommended_flow_duration_s}s",
            (
                f"{scene.selected_flow_duration_s}s"
                if scene.selected_flow_duration_s is not None
                else "Belum dipilih"
            ),
            _status_text(scene.readiness),
        )
        for column, value in enumerate(values):
            _set_cell(table, row, column, value)

    for label in root.findChildren(QLabel):
        if label.text() == "60/60 scene valid":
            if workspace.blocking_count:
                label.setText(
                    f"{workspace.blocking_count}/{len(workspace.scenes)} scene perlu diperbaiki"
                )
            else:
                label.setText(f"{len(workspace.scenes)}/{len(workspace.scenes)} scene valid")
        elif "Durasi rekomendasi bukan pilihan final" in label.text():
            label.setText(
                f"{workspace.duration_selection_count} scene menunggu pilihan Durasi Flow. "
                "Rekomendasi dihitung ulang dari Target."
            )

    _button(root, "Buat Workspace").clicked.connect(on_create)
    _button(root, "Batal").clicked.connect(on_cancel)
    return root


def build_workspace_view(workspace: WorkspaceState) -> QWidget:
    """Render persisted real scene rows in the frozen ready-workspace screen."""

    root = build_screen(get_fixture("UI-IMG-002A"))
    table = _table_with_columns(root, 9)
    table.setRowCount(len(workspace.scenes))

    for row, scene in enumerate(workspace.scenes):
        flow_value = (
            f"{scene.selected_flow_duration_s}s"
            if scene.selected_flow_duration_s is not None
            else f"{scene.recommended_flow_duration_s}s • rekom."
        )
        image_value = "Auto • Approved" if scene.image_exists else _status_text(scene.readiness)
        values = (
            _display_scene_id(scene.scene_id),
            image_value,
            scene.motion_prompt,
            f"{scene.target_duration_s:.2f}s",
            flow_value,
            "Belum ditetapkan",
            "Belum",
            "Belum",
            _status_text(scene.readiness),
        )
        for column, value in enumerate(values):
            _set_cell(table, row, column, value)

    if workspace.scenes:
        table.setCurrentCell(0, 0)

    for label in root.findChildren(QLabel):
        text = label.text()
        if text.startswith("Paket biography tersinkron"):
            label.setText("Paket episode tersinkron • state workspace nyata")
        elif "60 scene • approved image auto-mapped" in text:
            label.setText(
                f"{len(workspace.scenes)} scene • approved image tervalidasi • "
                f"{workspace.model} • {workspace.resolution} • {workspace.aspect_ratio}"
            )
        elif text == "60 scene • 60 siap":
            label.setText(
                f"{len(workspace.scenes)} scene • {workspace.ready_count} siap • "
                f"{workspace.duration_selection_count} pilih durasi • "
                f"{workspace.blocking_count} bermasalah"
            )
    return root


def build_workspace_right_panel(workspace: WorkspaceState) -> QWidget | None:
    """Render the frozen Scene/Agent dock with the first real scene selected."""

    panel = build_right_panel(get_fixture("UI-IMG-002A"))
    if panel is None or not workspace.scenes:
        return panel

    scene = workspace.scenes[0]
    replacements = {
        "S016": _display_scene_id(scene.scene_id),
        "7.32s": f"{scene.target_duration_s:.2f}s",
        "8s": f"{scene.recommended_flow_duration_s}s",
    }
    for label in panel.findChildren(QLabel):
        if label.text() in replacements:
            label.setText(replacements[label.text()])

    prompts = panel.findChildren(QPlainTextEdit)
    if prompts:
        prompts[0].setPlainText(scene.motion_prompt)
    return panel
