from __future__ import annotations

import time
from dataclasses import replace
from datetime import UTC, datetime
from threading import Event, Lock

import pytest
from PySide6.QtCore import Qt, QThreadPool, QTimer
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton

from flow_otomatis.application.services.gemini_agent import GeminiAgentReply
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.presentation.main_window import MainWindow


class SlowFakeAgentService:
    def ask(
        self,
        workspace: WorkspaceState,
        scene_id: str,
        question: str,
    ) -> GeminiAgentReply:
        assert workspace.episode_id == "EP_AGENT_UI"
        assert scene_id == "SCENE_001"
        assert question == "Scene ini siap?"
        time.sleep(0.12)
        return GeminiAgentReply(
            text="Ya. Scene ini siap berdasarkan state lokal yang tersedia.",
            model="gemini-3.8-flash",
            key_label="Gemini Fixture",
        )


def _workspace() -> WorkspaceState:
    now = datetime.now(UTC)
    return WorkspaceState(
        schema_version="1.0",
        episode_id="EP_AGENT_UI",
        project_name="Agent UI",
        source_package_path="fixture.zip",
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(
            WorkspaceScene(
                scene_id="SCENE_001",
                image_file="SCENE_001.png",
                image_exists=True,
                motion_prompt="Slow push in.",
                target_duration_s=4.0,
                recommended_flow_duration_s=4,
                selected_flow_duration_s=4,
                readiness=SceneReadiness.READY,
                trim_target_s=4.0,
                model="Omni Flash 1.1",
                resolution="720p",
                aspect_ratio="16:9",
            ),
        ),
    )


def test_dynamic_agent_answer_is_async_and_keeps_qt_heartbeat(qtbot) -> None:
    window = MainWindow(gemini_agent_service=SlowFakeAgentService())  # type: ignore[arg-type]
    qtbot.addWidget(window)
    window.show_workspace_state(_workspace())

    inputs = [
        item
        for item in window.findChildren(QLineEdit)
        if "Tanyakan status project" in item.placeholderText()
    ]
    assert inputs
    agent_input = inputs[0]
    send = next(button for button in window.findChildren(QPushButton) if button.text() == "Kirim")

    heartbeat: list[int] = []
    timer = QTimer(window)
    timer.setInterval(10)
    timer.timeout.connect(lambda: heartbeat.append(len(heartbeat) + 1))
    timer.start()

    agent_input.setText("Scene ini siap?")
    send.click()
    # Windows CI can delay Qt timers under heavy build load. Await the actual
    # heartbeat rather than requiring two events in a fixed 80 ms slice.
    qtbot.waitUntil(lambda: len(heartbeat) >= 2, timeout=1000)

    qtbot.waitUntil(
        lambda: any(
            "Scene ini siap berdasarkan state lokal" in label.text()
            for label in window.findChildren(QLabel)
        ),
        timeout=1500,
    )
    assert window.fixture_code == "REAL_WORKSPACE"


class OrderedFakeAgentService:
    def __init__(self) -> None:
        self.lock = Lock()
        self.entered: dict[tuple[str, str], Event] = {}
        self.release: dict[tuple[str, str], Event] = {}
        self.exited: dict[tuple[str, str], Event] = {}

    def register(self, episode_id: str, scene_id: str) -> None:
        key = (episode_id, scene_id)
        self.entered[key] = Event()
        self.release[key] = Event()
        self.exited[key] = Event()

    def ask(self, workspace: WorkspaceState, scene_id: str, question: str) -> GeminiAgentReply:
        key = (workspace.episode_id, scene_id)
        self.entered[key].set()
        assert self.release[key].wait(5), "Agent request was not released"
        self.exited[key].set()
        if question == "fail":
            from flow_otomatis.domain.errors import FlowOtomatisError

            raise FlowOtomatisError("fixture error")
        return GeminiAgentReply(
            text=f"ANSWER {workspace.episode_id} {scene_id}",
            model="gemini-3.8-flash",
            key_label="Fixture",
        )


def _two_scenes() -> WorkspaceState:
    original = _workspace()
    first = original.scenes[0]
    return replace(
        original,
        scenes=(first, replace(first, scene_id="SCENE_002", image_file="SCENE_002.png")),
    )


@pytest.mark.parametrize("old_question", ["normal", "fail"])
def test_t05_t06_stale_agent_completion_cannot_replace_next_scene_or_unlock_busy(
    qtbot,
    old_question: str,
) -> None:
    service = OrderedFakeAgentService()
    a = ("EP_AGENT_UI", "SCENE_001")
    b = ("EP_AGENT_UI", "SCENE_002")
    service.register(*a)
    service.register(*b)
    window = MainWindow(gemini_agent_service=service)  # type: ignore[arg-type]
    qtbot.addWidget(window)
    window.show_workspace_state(_two_scenes())
    window._ask_gemini_agent(old_question)
    try:
        qtbot.waitUntil(lambda: service.entered[a].is_set(), timeout=2500)
        window.select_workspace_scene("SCENE_002")
        window._ask_gemini_agent("current")
        qtbot.waitUntil(lambda: service.entered[b].is_set(), timeout=2500)
        active_b = window._active_agent_request
        assert active_b is not None
        service.release[a].set()
        qtbot.waitUntil(lambda: service.exited[a].is_set(), timeout=2500)
        # Process pending Qt signals while request B remains blocked.
        qtbot.wait(60)
        assert window._active_agent_request == active_b
        assert window._agent_busy
        assert window._agent_answer is None

        service.release[b].set()
        qtbot.waitUntil(
            lambda: window._agent_answer == "ANSWER EP_AGENT_UI SCENE_002",
            timeout=2500,
        )
        assert not window._agent_busy
    finally:
        service.release[a].set()
        service.release[b].set()
        QThreadPool.globalInstance().waitForDone(5000)


def test_t07_same_scene_id_in_other_project_does_not_receive_old_answer(qtbot) -> None:
    service = OrderedFakeAgentService()
    a = ("EP_AGENT_UI", "SCENE_001")
    b = ("EP_OTHER", "SCENE_001")
    service.register(*a)
    service.register(*b)
    window = MainWindow(gemini_agent_service=service)  # type: ignore[arg-type]
    qtbot.addWidget(window)
    window.show_workspace_state(_workspace())
    window._ask_gemini_agent("old")
    try:
        qtbot.waitUntil(lambda: service.entered[a].is_set(), timeout=2500)
        window.show_workspace_state(
            replace(_workspace(), episode_id="EP_OTHER", project_name="Other Project")
        )
        window._ask_gemini_agent("new")
        qtbot.waitUntil(lambda: service.entered[b].is_set(), timeout=2500)
        service.release[a].set()
        qtbot.waitUntil(lambda: service.exited[a].is_set(), timeout=2500)
        qtbot.wait(60)
        assert window._agent_busy
        assert window._agent_answer is None
        service.release[b].set()
        qtbot.waitUntil(lambda: window._agent_answer == "ANSWER EP_OTHER SCENE_001", timeout=2500)
    finally:
        service.release[a].set()
        service.release[b].set()
        QThreadPool.globalInstance().waitForDone(5000)


def test_t08_close_window_during_agent_request_does_not_touch_destroyed_receiver(
    qtbot,
) -> None:
    service = OrderedFakeAgentService()
    key = ("EP_AGENT_UI", "SCENE_001")
    service.register(*key)
    window = MainWindow(gemini_agent_service=service)  # type: ignore[arg-type]
    qtbot.addWidget(window)
    window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    window.show_workspace_state(_workspace())
    window._ask_gemini_agent("after close")
    try:
        qtbot.waitUntil(lambda: service.entered[key].is_set(), timeout=2500)
        window.close()
        service.release[key].set()
        assert QThreadPool.globalInstance().waitForDone(5000)
        qtbot.wait(60)
    finally:
        service.release[key].set()
