"""Bind real local result state to the frozen Hasil compositions."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QWidget

from flow_otomatis.domain.job import GenerationJobState
from flow_otomatis.domain.result import DownloadState, ProjectResults
from flow_otomatis.presentation.fixtures import get_fixture
from flow_otomatis.presentation.screen_factory import build_screen


def _display_scene_id(scene_id: str) -> str:
    return scene_id.replace("SCENE_", "S", 1)


def _generate_text(state: GenerationJobState | None) -> str:
    return {
        None: "Belum",
        GenerationJobState.QUEUED: "Menunggu",
        GenerationJobState.RUNNING: "Sedang Diproses",
        GenerationJobState.GENERATED: "Selesai",
        GenerationJobState.ATTENTION_REQUIRED: "Perlu Perhatian",
        GenerationJobState.FAILED: "Gagal",
    }[state]


def _download_text(state: str) -> str:
    return {
        DownloadState.NOT_DOWNLOADED: "Belum",
        DownloadState.DOWNLOADED: "Tersimpan",
        DownloadState.FAILED: "Gagal",
    }.get(state, state)


def _fixture_code(results: ProjectResults) -> str:
    if results.handoff_ready:
        return "UI-IMG-003C"
    if results.attention_count:
        return "UI-IMG-003B"
    return "UI-IMG-003A"


def _results_table(root: QWidget) -> QTableWidget:
    for table in root.findChildren(QTableWidget):
        if table.columnCount() == 6:
            return table
    raise RuntimeError("Frozen Hasil view is missing the six-column result table")


def _set_metric(root: QWidget, title: str, value: str) -> None:
    for frame in root.findChildren(QFrame):
        labels = frame.findChildren(QLabel)
        texts = [label.text() for label in labels]
        if title not in texts:
            continue
        title_index = texts.index(title)
        if title_index + 1 < len(labels):
            labels[title_index + 1].setText(value)
        return


def build_results_view(
    results: ProjectResults,
    *,
    on_export_manifest: Callable[[], object],
) -> QWidget:
    """Render real Generate/Download facts inside the frozen Hasil screen."""

    root = build_screen(get_fixture(_fixture_code(results)))
    table = _results_table(root)
    table.setRowCount(len(results.scenes))

    for row, scene in enumerate(results.scenes):
        values = (
            _display_scene_id(scene.scene_id),
            f"{scene.target_duration_s:.2f}s",
            (
                f"{scene.selected_flow_duration_s}s"
                if scene.selected_flow_duration_s is not None
                else "—"
            ),
            _generate_text(scene.generate_state),
            _download_text(scene.download_state),
            Path(scene.output_path).name if scene.output_path else "—",
        )
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(value))

    total = len(results.scenes)
    _set_metric(root, "Generate", f"{results.generated_count}/{total}")
    _set_metric(root, "Download", f"{results.downloaded_count}/{total}")
    _set_metric(root, "Perhatian", str(results.attention_count))

    for label in root.findChildren(QLabel):
        if label.text().startswith("60/60 video generated"):
            label.setText(
                f"{results.generated_count}/{total} video generated • "
                f"{results.downloaded_count}/{total} video downloaded • "
                "FLOW_OTOMATIS_RESULT.json siap diekspor."
            )

    if results.handoff_ready:
        for button in root.findChildren(QPushButton):
            if button.text() == "Tandai Siap untuk Editing":
                button.clicked.connect(on_export_manifest)
                break
    return root
