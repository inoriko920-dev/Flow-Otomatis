"""Read-only preflight report for persisted Workspace inputs (never live queue)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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

from flow_otomatis.application.services.local_scene_preflight import (
    prepare_local_scene_preflight,
)
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.presentation import theme


class LocalScenePreflightDialog(QDialog):
    """Exhibit the non-executable preview without using any queue provider."""

    def __init__(self, workspace: WorkspaceState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LocalScenePreflightDialog")
        self.setWindowTitle("Preflight Antrean Scene Lokal — Baca Saja")
        self.setMinimumSize(850, 530)
        self.resize(1050, 640)
        self.setStyleSheet(theme.application_stylesheet())
        self.report: dict[str, Any] = prepare_local_scene_preflight(workspace)

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
        self.table = QTableWidget(len(rows), 5)
        self.table.setObjectName("LocalPreflightTable")
        self.table.setHorizontalHeaderLabels(
            ["Scene", "Target", "Flow Terpilih", "Kondisi", "Perbaikan Diperlukan"]
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
            ]
            for col_index, value in enumerate(items):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
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
