"""Read-only preflight report for persisted Workspace inputs (never live queue)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.application.ports.episode_package import EpisodeImageVerifierPort
from flow_otomatis.application.services.local_scene_preflight import (
    prepare_local_scene_preflight,
)
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.presentation import theme


class _ImageScanSignals(QObject):
    completed = Signal(object)
    failed = Signal()


class _ImageScanTask(QRunnable):
    """Read source images outside the GUI thread; never enqueue provider work."""

    def __init__(
        self,
        workspace: WorkspaceState,
        verifier: EpisodeImageVerifierPort,
        signals: _ImageScanSignals,
    ) -> None:
        super().__init__()
        self._workspace = workspace
        self._verifier = verifier
        self._signals = signals

    @Slot()
    def run(self) -> None:
        try:
            report = prepare_local_scene_preflight(
                self._workspace, image_verifier=self._verifier
            )
        except Exception:
            self._signals.failed.emit()
        else:
            self._signals.completed.emit(report)


class LocalScenePreflightDialog(QDialog):
    """Exhibit a non-executable preflight; optional byte scan stays local-only."""

    def __init__(
        self,
        workspace: WorkspaceState,
        parent: QWidget | None = None,
        *,
        image_verifier: EpisodeImageVerifierPort | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("LocalScenePreflightDialog")
        self.setWindowTitle("Preflight Antrean Scene Lokal — Baca Saja")
        self.setMinimumSize(850, 530)
        self.resize(1050, 640)
        self.setStyleSheet(theme.application_stylesheet())
        self.report: dict[str, Any] = prepare_local_scene_preflight(workspace)
        self._workspace = workspace
        self._verifier = image_verifier
        self._checking_images = False
        self._scan_signals: _ImageScanSignals | None = None
        self._requested_scene_id: str | None = None

        layout = QVBoxLayout(self)
        heading = QLabel("Pemeriksaan Sebelum Menyusun Antrean")
        heading.setObjectName("LocalPreflightHeading")
        heading.setStyleSheet("font-size: 16pt; font-weight: 700;")
        layout.addWidget(heading)
        self.summary = QLabel(
            f"{self.report['total_scenes']} Scene • "
            f"{self.report['ready_count']} siap input lokal • "
            f"{self.report['held_count']} ditahan"
        )
        self.summary.setObjectName("LocalPreflightSummary")
        layout.addWidget(self.summary)

        caution = QLabel(str(self.report["warning"]))
        caution.setObjectName("LocalPreflightWarning")
        caution.setWordWrap(True)
        caution.setStyleSheet(
            "background: #fff7ed; color: #9a3412; "
            "padding: 12px; border: 1px solid #fed7aa; border-radius: 6px;"
        )
        layout.addWidget(caution)

        rows = [*self.report["ready"], *self.report["held"]]
        self.table = QTableWidget(len(rows), 6)
        self.table.setObjectName("LocalPreflightTable")
        self.table.setHorizontalHeaderLabels(
            [
                "Scene",
                "Target",
                "Flow Terpilih",
                "Kondisi",
                "Perbaikan Diperlukan",
                "Bukti Byte Gambar",
            ]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        for row_index, row in enumerate(rows):
            items = [
                row["scene_id"],
                f"{row['target_duration_s']:g}s"
                if row["target_duration_s"] is not None
                else "INVALID",
                f"{row['flow_duration_s']}s"
                if row["flow_duration_s"] is not None
                else "Belum valid",
                row["status"],
                "; ".join(row["issues"]) if row["issues"] else "Tidak ada",
                row["image_evidence"],
            ]
            for col_index, value in enumerate(items):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()
        self.table.itemSelectionChanged.connect(self._update_open_scene_action)
        layout.addWidget(self.table, 1)

        self.image_check_status = QLabel("Pemeriksaan byte gambar belum dijalankan.")
        self.image_check_status.setObjectName("LocalImageCheckStatus")
        self.image_check_status.setWordWrap(True)
        layout.addWidget(self.image_check_status)
        actions = QHBoxLayout()
        self.verify_button = QPushButton("Periksa Byte Gambar (SHA-256)")
        self.verify_button.setObjectName("LocalPreflightVerifyImages")
        self.verify_button.setEnabled(image_verifier is not None)
        self.verify_button.setToolTip(
            "Baca file paket sumber secara lokal, tidak memanggil Google Flow."
        )
        self.verify_button.clicked.connect(self.verify_source_images)
        actions.addWidget(self.verify_button)
        self.open_scene_button = QPushButton("Buka Scene Terpilih di Workspace")
        self.open_scene_button.setObjectName("LocalPreflightOpenScene")
        self.open_scene_button.setEnabled(False)
        self.open_scene_button.clicked.connect(self._request_open_scene)
        actions.addWidget(self.open_scene_button)
        self.export_button = QPushButton("Ekspor Hasil Preflight JSON")
        self.export_button.setObjectName("LocalPreflightExport")
        self.export_button.clicked.connect(self.export_json)
        actions.addWidget(self.export_button)
        actions.addStretch(1)
        close = QPushButton("Tutup")
        close.setObjectName("LocalPreflightClose")
        close.clicked.connect(self.accept)
        actions.addWidget(close)
        layout.addLayout(actions)
        if rows:
            self.table.setCurrentCell(0, 0)
            self._update_open_scene_action()

    @property
    def requested_scene_id(self) -> str | None:
        """An explicitly chosen, uniquely identifiable local Scene or None."""
        return self._requested_scene_id

    def _selected_scene_id(self) -> str | None:
        """Never navigate to duplicate/malformed IDs or fabricated report rows."""
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if item is None or self.table.isRowHidden(row):
            return None
        scene_id = item.text()
        matches = sum(scene.scene_id == scene_id for scene in self._workspace.scenes)
        if matches != 1:
            return None
        return scene_id

    def _update_open_scene_action(self) -> None:
        self.open_scene_button.setEnabled(
            not self._checking_images and self._selected_scene_id() is not None
        )

    def _request_open_scene(self) -> None:
        target = self._selected_scene_id()
        if target is None:
            return
        self._requested_scene_id = target
        self.accept()

    def verify_source_images(self) -> None:
        """Start an opt-in, filesystem-only scan on a Qt background worker."""
        if self._verifier is None or self._checking_images:
            return
        self._checking_images = True
        self.verify_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.open_scene_button.setEnabled(False)
        self.image_check_status.setText("Membaca sumber gambar lokal…")
        signals = _ImageScanSignals()
        signals.completed.connect(self._image_scan_complete)
        signals.failed.connect(self._image_scan_failed)
        self._scan_signals = signals
        QThreadPool.globalInstance().start(
            _ImageScanTask(self._workspace, self._verifier, signals)
        )

    @Slot(object)
    def _image_scan_complete(self, report: object) -> None:
        if not self._checking_images or not isinstance(report, dict):
            return
        self.report = report
        self._checking_images = False
        self.verify_button.setEnabled(self._verifier is not None)
        self.export_button.setEnabled(True)
        self._show_report()
        self.image_check_status.setText(
            f"Gambar dengan byte terbaca: {report['verified_image_count']}; "
            f"tidak terbaca: {report['unreadable_image_count']}. "
            "Ini tidak membuktikan isi gambar belum berubah sejak diimpor."
        )
        self._scan_signals = None

    @Slot()
    def _image_scan_failed(self) -> None:
        self._checking_images = False
        self.verify_button.setEnabled(self._verifier is not None)
        self.export_button.setEnabled(True)
        self._update_open_scene_action()
        self.image_check_status.setText(
            "Pemeriksaan file gagal. Hasil sebelumnya masih metadata saja; "
            "jangan anggap byte gambar terverifikasi."
        )
        self._scan_signals = None

    def _show_report(self) -> None:
        """Refresh noneditable rows while keeping Scene navigability guarded."""
        report = self.report
        self.summary.setText(
            f"{report['total_scenes']} Scene • "
            f"{report['ready_count']} siap input lokal • "
            f"{report['held_count']} ditahan"
        )
        rows = [*report["ready"], *report["held"]]
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = (
                row["scene_id"],
                f"{row['target_duration_s']:g}s"
                if row["target_duration_s"] is not None
                else "INVALID",
                f"{row['flow_duration_s']}s"
                if row["flow_duration_s"] is not None
                else "Belum valid",
                row["status"],
                "; ".join(row["issues"]) if row["issues"] else "Tidak ada",
                row["image_evidence"],
            )
            for col_index, value in enumerate(values):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
        if rows:
            self.table.setCurrentCell(0, 0)
        else:
            self.table.clearSelection()
        self._update_open_scene_action()

    def export_json(self) -> None:
        """Create-only report; never overwrite a previous audit/export."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan hasil pemeriksaan lokal",
            "preflight_scene_lokal.json",
            "JSON (*.json)",
        )
        if not filename:
            return
        try:
            with Path(filename).open("x", encoding="utf-8") as stream:
                json.dump(self.report, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.write("\n")
        except FileExistsError:
            QMessageBox.warning(self, "Tidak ditimpa", "File yang sudah ada tidak diubah.")
        except OSError:
            QMessageBox.warning(
                self,
                "Tidak dapat menyimpan",
                "Periksa folder dan izin akses, lalu simpan ke lokasi lain.",
            )
