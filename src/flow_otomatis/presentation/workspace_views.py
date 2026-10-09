"""Bind real workspace state to the frozen STEP 09 presentation."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QWidget,
)

from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import FLOW_DURATIONS, SceneReadiness, WorkspaceScene
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


def build_workspace_view(
    workspace: WorkspaceState,
    *,
    on_rescan_images: Callable[[], object],
    on_scene_selected: Callable[[str], object],
    on_preview_credit_ui: Callable[[], object] | None = None,
    selected_scene_id: str | None = None,
) -> QWidget:
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
        index = next(
            (
                index
                for index, scene in enumerate(workspace.scenes)
                if scene.scene_id == selected_scene_id
            ),
            0,
        )
        table.setCurrentCell(index, 0)

    def notify_selected(row: int, _column: int) -> None:
        if 0 <= row < len(workspace.scenes):
            on_scene_selected(workspace.scenes[row].scene_id)

    table.cellClicked.connect(notify_selected)
    scan_button = _button(root, "Scan Ulang Gambar")
    scan_button.clicked.connect(on_rescan_images)
    if on_preview_credit_ui is not None:
        # Add only to the real Workspace controls; frozen reference views remain unchanged.
        toolbar_parent = scan_button.parentWidget()
        if toolbar_parent is None:
            raise RuntimeError("Workspace controls parent is missing")
        action_row = toolbar_parent.layout()
        if action_row is None:
            raise RuntimeError("Workspace controls layout is missing")
        preview_button = QPushButton("Pratinjau 22 UI Multiakun (Simulasi)")
        preview_button.setObjectName("UixPreviewWorkspaceAction")
        action_row.addWidget(preview_button)
        preview_button.clicked.connect(on_preview_credit_ui)

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


def _scene_by_id(workspace: WorkspaceState, scene_id: str) -> WorkspaceScene:
    for scene in workspace.scenes:
        if scene.scene_id == scene_id:
            return scene
    return workspace.scenes[0]


def build_workspace_right_panel(
    workspace: WorkspaceState,
    *,
    scene_id: str,
    on_select_duration: Callable[[int], object],
    on_agent_question: Callable[[str], object] | None = None,
    agent_answer: str | None = None,
    agent_busy: bool = False,
) -> QWidget | None:
    """Render frozen Scene/Agent dock for the selected persisted Scene."""

    panel = build_right_panel(get_fixture("UI-IMG-002A"))
    if panel is None or not workspace.scenes:
        return panel

    scene = _scene_by_id(workspace, scene_id)
    replacements = {
        "S016": _display_scene_id(scene.scene_id),
        "7.32s": f"{scene.target_duration_s:.2f}s",
        "8s": f"{scene.recommended_flow_duration_s}s",
        "APPROVED IMAGE\nSCENE_016": (
            f"APPROVED IMAGE\n{scene.scene_id}"
            if scene.image_exists
            else f"MISSING IMAGE\n{scene.scene_id}"
        ),
        "Auto-mapped • Approved": (
            "Auto-mapped • Approved" if scene.image_exists else "Gambar Hilang"
        ),
    }
    for label in panel.findChildren(QLabel):
        if label.text() in replacements:
            label.setText(replacements[label.text()])

    prompts = panel.findChildren(QPlainTextEdit)
    if prompts:
        prompts[0].setPlainText(scene.motion_prompt)

    for button in panel.findChildren(QPushButton):
        raw = button.text().removesuffix("s")
        if not raw.isdigit():
            continue
        duration = int(raw)
        if duration not in FLOW_DURATIONS:
            continue
        button.setEnabled(duration + 1e-9 >= scene.target_duration_s)
        is_selected = scene.selected_flow_duration_s == duration
        is_recommended = scene.selected_flow_duration_s is None and (
            scene.recommended_flow_duration_s == duration
        )
        button.setObjectName("Primary" if is_selected or is_recommended else "")
        button.clicked.connect(lambda _checked=False, value=duration: on_select_duration(value))

    agent_inputs = panel.findChildren(QLineEdit)
    agent_input = agent_inputs[0] if agent_inputs else None
    send_button = next(
        (button for button in panel.findChildren(QPushButton) if button.text() == "Kirim"),
        None,
    )
    answer_label = next(
        (
            label
            for label in panel.findChildren(QLabel)
            if label.text().startswith("Saya siap membantu membaca status project")
        ),
        None,
    )
    display_answer = (
        "Sedang menganalisis status project…"
        if agent_busy
        else (
            agent_answer
            or "Saya siap membantu membaca status project dan mengusulkan tindakan yang aman."
        )
    )
    if answer_label is not None:
        answer_label.setText(display_answer[:2400])
        answer_label.setWordWrap(True)

    def submit_agent_question() -> None:
        if on_agent_question is None or agent_input is None or agent_busy:
            return
        question = agent_input.text().strip()
        if question:
            on_agent_question(question)

    if agent_input is not None:
        agent_input.setEnabled(not agent_busy)
        if on_agent_question is not None:
            agent_input.returnPressed.connect(submit_agent_question)
    if send_button is not None:
        send_button.setEnabled(not agent_busy and on_agent_question is not None)
        if on_agent_question is not None:
            send_button.clicked.connect(submit_agent_question)

    if agent_busy or agent_answer:
        tabs = panel if isinstance(panel, QTabWidget) else panel.findChild(QTabWidget)
        if tabs is not None and tabs.count() > 1:
            tabs.setCurrentIndex(1)
    return panel
