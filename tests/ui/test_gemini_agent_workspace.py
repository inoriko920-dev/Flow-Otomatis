from __future__ import annotations

import threading
from datetime import UTC, datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton

from flow_otomatis.domain.gemini import GeminiAgentAction, GeminiAgentReply
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness, WorkspaceScene
from flow_otomatis.presentation.main_window import MainWindow


class SlowAgentService:
    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()

    def ask(self, context, user_message):
        assert context.scene_id == "SCENE_001"
        assert user_message == "Apa langkah berikutnya?"
        self.started.set()
        assert self.release.wait(timeout=2.0)
        return GeminiAgentReply(
            message="Scene sudah siap. Periksa Hasil setelah Generate selesai.",
            action=GeminiAgentAction.OPEN_RESULTS,
            rationale="Status lokal Scene sudah READY.",
        )


def _workspace() -> WorkspaceState:
    now = datetime.now(UTC)
    scene = WorkspaceScene(
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
    )
    return WorkspaceState(
        schema_version="1.0",
        episode_id="EP_AGENT",
        project_name="Agent UI",
        source_package_path="package.zip",
        created_at=now,
        imported_at=now,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
        scenes=(scene,),
    )


def test_slow_agent_keeps_qt_heartbeat_and_only_displays_proposal(qtbot) -> None:
    service = SlowAgentService()
    window = MainWindow(gemini_agent_service=service)  # type: ignore[arg-type]
    qtbot.addWidget(window)
    window.show_workspace_state(_workspace())

    inputs = [
        item
        for item in window.findChildren(QLineEdit)
        if "Tanyakan status project" in item.placeholderText()
    ]
    assert len(inputs) == 1
    send = next(button for button in window.findChildren(QPushButton) if button.text() == "Kirim")
    inputs[0].setText("Apa langkah berikutnya?")

    heartbeat: list[int] = []
    timer = QTimer(window)
    timer.setInterval(10)
    timer.timeout.connect(lambda: heartbeat.append(len(heartbeat) + 1))
    timer.start()

    send.click()
    assert service.started.wait(timeout=1.0)
    qtbot.wait(120)
    assert len(heartbeat) >= 3

    service.release.set()
    qtbot.waitUntil(
        lambda: any("Scene sudah siap" in label.text() for label in window.findChildren(QLabel)),
        timeout=1500,
    )
    visible = " ".join(label.text() for label in window.findChildren(QLabel))
    assert "Usulan tindakan: OPEN_RESULTS" in visible
    assert "Belum dijalankan otomatis." in visible
