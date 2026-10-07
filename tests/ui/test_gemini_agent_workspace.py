from __future__ import annotations

import time
from datetime import UTC, datetime

from PySide6.QtCore import QTimer
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
    qtbot.wait(80)
    assert len(heartbeat) >= 2

    qtbot.waitUntil(
        lambda: any(
            "Scene ini siap berdasarkan state lokal" in label.text()
            for label in window.findChildren(QLabel)
        ),
        timeout=1500,
    )
    assert window.fixture_code == "REAL_WORKSPACE"
