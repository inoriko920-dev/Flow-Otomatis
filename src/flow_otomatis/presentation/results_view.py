"""Bind real local result state to the frozen Hasil compositions."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.domain.job import GenerationJobState
from flow_otomatis.domain.result import DownloadState, ProjectResults
from flow_otomatis.presentation.fixtures import get_fixture
from flow_otomatis.presentation.screen_factory import build_screen
from flow_otomatis.presentation.widgets import info_banner, page_header, primary_button


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
        DownloadState.UNAVAILABLE: "Tidak Tersedia",
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


def _set_metric(root: QWidget, title: str, value: str, detail: str) -> None:
    for frame in root.findChildren(QFrame):
        labels = frame.findChildren(QLabel, options=Qt.FindChildOption.FindDirectChildrenOnly)
        if len(labels) == 3 and labels[0].text() == title:
            labels[1].setText(value)
            labels[2].setText(detail)
            return
    raise RuntimeError(f"Frozen Hasil card missing metric: {title}")


def build_results_service_unavailable_view(
    *,
    on_workspace: Callable[[], object],
) -> QWidget:
    """Active local project without a configured result reader is NOT success."""

    root = QWidget()
    root.setObjectName("RealResultsUnavailable")
    layout = QVBoxLayout(root)
    layout.setContentsMargins(22, 18, 22, 18)
    layout.setSpacing(16)
    layout.addWidget(page_header("Hasil", "Data hasil proyek lokal belum dapat diperiksa"))
    layout.addWidget(
        info_banner(
            "PEMBACA HASIL TIDAK TERSEDIA",
            "Workspace sudah dipilih, tetapi komponen pembaca riwayat Generate "
            "dan Download belum tersedia. Tidak ada MP4 atau keberhasilan "
            "Generate yang dapat dikonfirmasi dari tampilan ini.",
            "warning",
        )
    )
    back = primary_button("Kembali ke Workspace")
    back.setObjectName("RealResultsUnavailableBack")
    back.clicked.connect(on_workspace)
    layout.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)
    layout.addStretch(1)
    return root


def build_results_view(
    results: ProjectResults,
    *,
    on_export_manifest: Callable[[], object],
    on_open_diagnostics: Callable[[], object] | None = None,
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
            (
                Path(scene.output_path).name
                if scene.download_state == DownloadState.DOWNLOADED and scene.output_path
                else "—"
            ),
        )
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(value))

    total = len(results.scenes)
    _set_metric(
        root,
        "Generate",
        f"{results.generated_count}/{total}",
        "Selesai" if total > 0 and results.generated_count == total else "Belum selesai",
    )
    _set_metric(
        root,
        "Download",
        f"{results.downloaded_count}/{total}",
        "Tersimpan" if results.handoff_ready else "Belum selesai",
    )
    _set_metric(
        root,
        "Perhatian",
        str(results.attention_count),
        "Perlu diperiksa" if results.attention_count else "Tidak ada laporan masalah",
    )

    for label in root.findChildren(QLabel):
        if label.text() == "Semua generation dan download selesai":
            label.setText("Status dari catatan proyek lokal • tidak mengakses Google Flow")
        if label.text().startswith("60/60 video generated"):
            label.setText(
                f"{results.generated_count}/{total} video generated • "
                f"{results.downloaded_count}/{total} video downloaded • "
                "FLOW_OTOMATIS_RESULT.json siap diekspor."
            )

    for button in root.findChildren(QPushButton):
        if button.text() == "Tandai Siap untuk Editing":
            button.setEnabled(results.handoff_ready)
            if results.handoff_ready:
                button.clicked.connect(on_export_manifest)
            else:
                button.setToolTip("Semua file hasil harus tersedia sebelum ekspor manifest.")
        elif button.text() == "Buka Diagnostik":
            # This is a real local-only route, not a Google Flow retry.
            button.setObjectName("RealResultsOpenDiagnostics")
            button.setEnabled(on_open_diagnostics is not None)
            if on_open_diagnostics is not None:
                button.clicked.connect(on_open_diagnostics)
                button.setToolTip("Periksa keadaan aplikasi dan proyek lokal.")
            else:
                button.setToolTip("Navigasi Diagnostik belum tersedia.")
        elif button.text() in {"Buka Folder Output", "Retry Download Terpilih"}:
            # No safe verified folder-open or retry action has been integrated.
            button.setEnabled(False)
            button.setToolTip("Aksi ini belum tersedia dari halaman hasil lokal.")
    return root
