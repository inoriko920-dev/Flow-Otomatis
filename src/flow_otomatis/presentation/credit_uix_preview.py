"""E12-02 Qt UI addendum: 22 owner-approved scenario states, offline preview only.

This preview preserves the existing seven-item sidebar. It has zero adapters to
Google Flow/Chrome, no credential access, no durable credit ledger and no live
Generate/Download controls. Simulated quantities are always labeled.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.application.services.offline_credit_simulation import simulate
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.presentation import theme
from flow_otomatis.presentation.widgets import (
    card,
    info_banner,
    metric_card,
    muted_label,
    page_header,
    primary_button,
    status_badge,
)


# Each entry corresponds to an exact, previously approved UIX state identifier.
# Examples are not quoted provider balances, actual remote results or entitlements.
@dataclass(frozen=True, slots=True)
class UixScenario:
    code: str
    title: str
    description: str
    severity: str
    banner: str
    detail: str


UIX_SCENARIOS: tuple[UixScenario, ...] = (
    UixScenario(
        "UIX-01-A",
        "Ringkasan Scan & Kredit",
        "Workspace • 12 scene, 10 siap, 2 perhatian",
        "info",
        "Scan lokal siap ditinjau",
        "Perencanaan kredit adalah simulasi, bukan saldo provider.",
    ),
    UixScenario(
        "UIX-01-B",
        "Input perlu diperbaiki",
        "Workspace • gambar, prompt, dan Target bermasalah",
        "warning",
        "3 scene perlu tindakan",
        (
            "SCENE_004 tanpa gambar, SCENE_007 tanpa prompt, "
            "SCENE_011 Target 11,2 detik. Jangan Generate."
        ),
    ),
    UixScenario(
        "UIX-01-C",
        "Tarif dan saldo belum terverifikasi",
        "Workspace • status kredit tidak diketahui",
        "warning",
        "Tarif tidak tersedia",
        (
            "Saldo akun dan kelayakan model belum dibuktikan. "
            "Bukan nol kredit; nilainya belum diketahui."
        ),
    ),
    UixScenario(
        "UIX-02-A",
        "Smart Credit Plan",
        "Dialog • 12 scene pada tiga profil sintetis",
        "info",
        "RENCANA SIMULASI — BELUM DISETUJUI",
        (
            "Periksa alokasi, estimasi kredit, Scene yang tertahan, "
            "dan batas belanja. Tidak mengirim permintaan."
        ),
    ),
    UixScenario(
        "UIX-02-B",
        "Kredit simulasi tidak mencukupi",
        "Dialog • subset Scene yang tidak teralokasikan",
        "warning",
        "Sebagian Scene tidak dialokasikan",
        "Hanya subset layak yang boleh ditinjau. Jangan memindahkan tugas untuk menghindari kuota.",
    ),
    UixScenario(
        "UIX-02-C",
        "Tidak ada akun memenuhi syarat",
        "Dialog • semua profil terblokir untuk live",
        "error",
        "Tidak ada akun terverifikasi",
        "Login bukan izin otomatisasi. Kebijakan, sesi, kredit, dan tarif semuanya wajib jelas.",
    ),
    UixScenario(
        "UIX-03-A",
        "Rincian Kredit per Akun",
        "Profil Google • laci informasi contoh",
        "info",
        "Contoh rincian kredit profil",
        "Angka 38 / 12 / 26 hanya ilustrasi. Status sumber ditampilkan sebagai DATA CONTOH.",
    ),
    UixScenario(
        "UIX-03-B",
        "Kredit kadaluarsa atau manual",
        "Profil Google • sumber tidak memenuhi verifikasi",
        "warning",
        "Jangan tampilkan saldo tidak diketahui sebagai 0",
        "Profil A kadaluarsa, Profil B angka manual, Profil C tidak diketahui. Live dinonaktifkan.",
    ),
    UixScenario(
        "UIX-04-A",
        "Freeze Plan & Approval",
        "Workspace • persetujuan revisi rencana",
        "info",
        "Tinjau sebelum mengunci versi simulasi",
        "Centang persetujuan hanya untuk mengunci pratinjau lokal, bukan melakukan Generate.",
    ),
    UixScenario(
        "UIX-04-B",
        "Rencana sudah kadaluarsa",
        "Workspace • perubahan gambar dan tarif",
        "warning",
        "Plan v3 tidak berlaku",
        (
            "SCENE_006, versi tarif dan bukti kredit berubah. "
            "Perlu hitung ulang, tanpa auto-reapproval."
        ),
    ),
    UixScenario(
        "UIX-05-A",
        "Run Monitor Simulasi",
        "Workspace • monitor aktivitas lokal",
        "info",
        "SIMULASI — TANPA GENERATE",
        "Contoh Profil A dan B menangani Scene terpisah. Tidak ada progres remote provider.",
    ),
    UixScenario(
        "UIX-05-B",
        "Monitor dijeda parsial",
        "Workspace • sebagian menunggu",
        "warning",
        "Jeda hanya menghentikan klaim baru",
        "Status Generate, Download, antrean, dan perhatian harus tetap dipisah.",
    ),
    UixScenario(
        "UIX-05-C",
        "Submit tidak pasti",
        "Workspace • status transaksi tidak diketahui",
        "warning",
        "SUBMIT_UNCERTAIN — cadangan tetap ditahan",
        "SCENE_008 Profil B tidak boleh dikirim ulang otomatis atau dipindah akun.",
    ),
    UixScenario(
        "UIX-06-A",
        "Recovery Submit Uncertain",
        "Pemulihan sementara • baca saja",
        "warning",
        "Periksa hasil tanpa menekan Generate",
        "Identitas remote belum ada; contoh cadangan kredit tetap HELD sampai bukti kuat.",
    ),
    UixScenario(
        "UIX-06-B",
        "Konflik login dan kredit",
        "Pemulihan sementara • akun per akun",
        "error",
        "Profil memerlukan perhatian manual",
        "Profil A perlu login manusia. Profil B kredit tidak memenuhi cadangan. Jangan lewati MFA.",
    ),
    UixScenario(
        "UIX-06-C",
        "Hasil Generate ditemukan",
        "Pemulihan sementara • rekonsiliasi contoh",
        "info",
        "Ditemukan bukti hasil simulasi",
        "ID hasil cocok hanya dalam ilustrasi. Download tetap terpisah dan belum selesai.",
    ),
    UixScenario(
        "UIX-07-A",
        "Partial Replan",
        "Workspace • Scene aman dapat direncanakan ulang",
        "info",
        "Hanya tugas yang belum dimutasi boleh diubah",
        "Empat Scene terkunci dalam ilustrasi; delapan tugas antre boleh dihitung ulang.",
    ),
    UixScenario(
        "UIX-07-B",
        "Scene terkunci",
        "Workspace • tidak boleh alih akun",
        "warning",
        "SCENE_003 terkunci — SUBMIT_UNCERTAIN",
        "Akun, input, dan reservasi lama tidak boleh dipindah tanpa bukti rekonsiliasi.",
    ),
    UixScenario(
        "UIX-08-A",
        "Tarif berubah",
        "Workspace • bukti harga kedaluwarsa",
        "warning",
        "Tarif vDEMO-1 → vDEMO-2",
        (
            "Perlu hitung ulang dan persetujuan baru. "
            "Ini contoh versi tarif, bukan daftar harga nyata."
        ),
    ),
    UixScenario(
        "UIX-08-B",
        "Kebijakan belum terverifikasi",
        "Workspace • pemblokiran aman",
        "error",
        "OTOMATISASI LIVE DIBLOKIR",
        "Belum ada bukti bahwa browser otomatis multiakun diperbolehkan provider.",
    ),
    UixScenario(
        "UIX-09-A",
        "Hasil Parsial",
        "Hasil • video dan checksum terpisah",
        "info",
        "Hasil contoh: tidak ada video provider yang diproduksi",
        "Bedakan Generated, Downloaded, File Lokal, dan Checksum. Angka mockup bukan hasil nyata.",
    ),
    UixScenario(
        "UIX-09-B",
        "Handoff VIDEO",
        "Hasil • contoh semua Scene selesai",
        "info",
        "Handoff 12/12 hanya ilustrasi",
        (
            "Output yang dimaksud VIDEO MP4 dan manifest JSON. "
            "Tidak ada file video asli dalam preview."
        ),
    ),
)

SCENARIO_BY_ID: dict[str, UixScenario] = {scenario.code: scenario for scenario in UIX_SCENARIOS}
GROUPS = (
    "UIX-01 • Scan",
    "UIX-02 • Smart Plan",
    "UIX-03 • Kredit",
    "UIX-04 • Freeze",
    "UIX-05 • Monitor",
    "UIX-06 • Recovery",
    "UIX-07 • Replan",
    "UIX-08 • Tarif/Policy",
    "UIX-09 • Hasil",
)

_DEMO_PLAN: dict[str, Any] = {
    "mode": "OFFLINE_SIMULATION",
    "profiles": [
        {"profile_id": "Profil-A", "simulated_balance": 45, "max_spend": 40},
        {"profile_id": "Profil-B", "simulated_balance": 35, "max_spend": 30},
        {"profile_id": "Profil-C", "simulated_balance": 20, "max_spend": 20},
    ],
    "scenes": [
        {
            "project_id": "DEMO_PROYEK",
            "scene_id": f"SCENE_{number:03}",
            "duration_s": (4, 6, 8, 10)[(number - 1) % 4],
            "outputs": 1,
        }
        for number in range(1, 13)
    ],
    "rates_per_video": {"4": 7, "6": 10, "8": 12, "10": 15},
    "max_total_credits": 90,
}


class CreditUixDialog(QDialog):
    """Interactive 22-state Qt preview of approved UI extension concepts."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        workspace: WorkspaceState | None = None,
        initial_state: str = "UIX-01-A",
    ) -> None:
        super().__init__(parent)
        self.setObjectName("CreditUixDialog")
        self.setWindowTitle("Flow-Otomatis | Pratinjau 22 UI Multiakun (Simulasi)")
        self.resize(1720, 960)
        self.setMinimumSize(1250, 740)
        self.setStyleSheet(theme.application_stylesheet())
        self._workspace = workspace
        self._preview = simulate(_DEMO_PLAN)
        self._current_state = "UIX-01-A"
        self._last_local_plan_approved = False

        # Recreate the frozen desktop app proportions inside the preview, rather
        # than presenting all 22 states as a plain floating table dialog.
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        rail = QFrame()
        rail.setObjectName("UixSidebar")
        rail.setFixedWidth(theme.SIDEBAR_WIDTH)
        rail.setStyleSheet(
            f"QFrame#UixSidebar {{ background: white; border-right: 1px solid {theme.BORDER}; }}"
        )
        rail_layout = QVBoxLayout(rail)
        rail_layout.setContentsMargins(14, 18, 14, 18)
        rail_layout.setSpacing(12)
        brand = QLabel("◈  Flow-Otomatis")
        brand.setObjectName("UixBrand")
        brand.setStyleSheet(f"font-size: 15pt; font-weight: 700; color: {theme.PRIMARY};")
        rail_layout.addWidget(brand)
        rail_layout.addWidget(muted_label("UIX22  •  Mode Simulasi"))
        rail_layout.addSpacing(12)
        for route in (
            "Beranda", "Workspace", "Hasil", "Profil Google",
            "Gemini Keys", "Diagnostik", "Pengaturan",
        ):
            item = QLabel("   " + route)
            item.setObjectName("UixSidebarRoute")
            item.setMinimumHeight(37)
            if route == "Workspace":
                item.setStyleSheet(
                    f"background: {theme.INFO_BG}; color: {theme.PRIMARY}; "
                    "font-weight: 600; border-radius: 6px;"
                )
            else:
                item.setStyleSheet("color: #475569;")
            rail_layout.addWidget(item)
        rail_layout.addStretch(1)
        rail_layout.addWidget(muted_label("Tidak mengubah proyek atau akun Google."))
        outer.addWidget(rail)

        center = QWidget()
        center.setObjectName("UixCenter")
        main = QVBoxLayout(center)
        main.setContentsMargins(17, 13, 17, 13)
        main.setSpacing(10)
        top = QHBoxLayout()
        top.addWidget(page_header("Workspace / Pratinjau Multiakun", "Omni Flash 1.1  •  720p  •  16:9"))
        top.addStretch(1)
        top.addWidget(status_badge("OFFLINE • DATA CONTOH", "warning"))
        main.addLayout(top)
        outer.addWidget(center, 1)

        dock = QFrame()
        dock.setObjectName("UixRightDock")
        dock.setFixedWidth(theme.RIGHT_DOCK_WIDTH)
        dock.setStyleSheet(
            f"QFrame#UixRightDock {{ background: white; border-left: 1px solid {theme.BORDER}; }}"
        )
        dock_layout = QVBoxLayout(dock)
        dock_layout.setContentsMargins(16, 20, 16, 20)
        dock_layout.setSpacing(12)
        dock_layout.addWidget(page_header("Scene & AI Agent", "Panel kanan • tidak terhubung"))
        dock_layout.addWidget(info_banner(
            "BACA SAJA",
            "Agent, login dan Generate tidak tersedia dalam pratinjau UI ini.",
            "info",
        ))
        dock_layout.addWidget(QLabel("KONDISI YANG DIPILIH"))
        self._dock_state = QLabel("UIX-01-A")
        self._dock_state.setObjectName("UixDockState")
        self._dock_state.setWordWrap(True)
        self._dock_state.setStyleSheet(f"font-weight: 600; color: {theme.PRIMARY};")
        dock_layout.addWidget(self._dock_state)
        dock_layout.addWidget(QLabel("PENGAMAN PRODUKSI"))
        for detail in (
            "• Durasi Flow: 4 / 6 / 8 / 10 detik",
            "• Target Audio/SRT tidak diubah",
            "• Kredit provider: tidak diketahui",
            "• Generate dan Download terpisah",
            "• Submit uncertain tidak diulang",
        ):
            dock_layout.addWidget(muted_label(detail))
        dock_layout.addStretch(1)
        dock_layout.addWidget(status_badge("LIVE DIBLOKIR", "error"))
        outer.addWidget(dock)

        main.addWidget(
            info_banner(
                "MODE SIMULASI • TIDAK TERHUBUNG GOOGLE FLOW",
                "Seluruh saldo, profil, status remote, dan biaya di panel ini adalah DATA CONTOH. "
                "Tidak ada login, Generate, Download, atau pengeluaran kredit.",
                "warning",
            )
        )

        navigation = QHBoxLayout()
        navigation.addWidget(QLabel("Kelompok UI"))
        self.group_selector = QComboBox()
        self.group_selector.setObjectName("UixGroupSelector")
        self.group_selector.addItems(GROUPS)
        navigation.addWidget(self.group_selector, 1)
        navigation.addWidget(QLabel("Kondisi"))
        self.state_selector = QComboBox()
        self.state_selector.setObjectName("UixStateSelector")
        navigation.addWidget(self.state_selector, 2)
        main.addLayout(navigation)
        self.group_selector.currentIndexChanged.connect(self._group_changed)
        self.state_selector.currentIndexChanged.connect(self._select_from_combo)

        self.scroller = QScrollArea()
        self.scroller.setWidgetResizable(True)
        self.scroller.setObjectName("UixPreviewScroll")
        main.addWidget(self.scroller, 1)
        self.footer = QHBoxLayout()
        self.status = muted_label("Simulasi saja • tanpa aksi provider")
        self.status.setObjectName("UixFooterStatus")
        self.footer.addWidget(self.status, 1)
        self.recompute_button = QPushButton("Hitung Ulang Simulasi")
        self.recompute_button.setObjectName("UixRecompute")
        self.recompute_button.clicked.connect(self.recalculate_offline)
        self.footer.addWidget(self.recompute_button)
        self.export_button = QPushButton("Simpan Laporan JSON")
        self.export_button.setObjectName("UixExport")
        self.export_button.clicked.connect(self.export_preview)
        self.footer.addWidget(self.export_button)
        close = QPushButton("Tutup")
        close.clicked.connect(self.accept)
        self.footer.addWidget(close)
        main.addLayout(self.footer)
        self._group_changed(0)
        self.set_state(initial_state)

    @property
    def current_state(self) -> str:
        return self._current_state

    @property
    def live_dispatch_enabled(self) -> bool:
        """Fail-closed public UI guard; no real provider is ever wired here."""
        return False

    def _group_changed(self, index: int) -> None:
        if index < 0:
            return
        prefix = f"UIX-{index + 1:02}-"
        current = self._current_state
        self.state_selector.blockSignals(True)
        self.state_selector.clear()
        for scenario in UIX_SCENARIOS:
            if scenario.code.startswith(prefix):
                self.state_selector.addItem(f"{scenario.code} · {scenario.title}", scenario.code)
        select = self.state_selector.findData(current)
        self.state_selector.setCurrentIndex(select if select >= 0 else 0)
        self.state_selector.blockSignals(False)
        chosen = self.state_selector.currentData()
        if chosen:
            self._render(chosen)

    def _select_from_combo(self, _index: int) -> None:
        code = self.state_selector.currentData()
        if code in SCENARIO_BY_ID:
            self._render(code)

    def set_state(self, code: str) -> None:
        """Navigate the 22 approved states without creating new sidebar routes."""
        if code not in SCENARIO_BY_ID:
            raise ValueError(f"Unknown UI reference state: {code}")
        index = int(code[4:6]) - 1
        if self.group_selector.currentIndex() != index:
            self.group_selector.setCurrentIndex(index)
        select = self.state_selector.findData(code)
        if select >= 0:
            self.state_selector.setCurrentIndex(select)
        self._render(code)

    def _render(self, code: str) -> None:
        scenario = SCENARIO_BY_ID[code]
        self._current_state = code
        self._dock_state.setText(f"{code} • {scenario.title}")
        self._last_local_plan_approved = False
        root = QWidget()
        root.setObjectName(f"UixPage{code.replace('-', '')}")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 4, 10, 12)
        layout.setSpacing(12)
        layout.addWidget(page_header(f"{scenario.code} · {scenario.title}", scenario.description))
        layout.addWidget(info_banner(scenario.banner, scenario.detail, scenario.severity))

        metrics = QGridLayout()
        metrics.setSpacing(10)
        figures = self._metrics_for(code)
        for index, (name, value, note, kind) in enumerate(figures):
            metrics.addWidget(metric_card(name, value, note, kind), 0, index)
        layout.addLayout(metrics)

        columns, rows = self._data_for(code)
        content, content_layout = card(7)
        content_layout.addWidget(self._section_title(code))
        table = QTableWidget(len(rows), len(columns))
        table.setObjectName("UixDetailTable")
        table.setHorizontalHeaderLabels(columns)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().hide()
        table.setMinimumHeight(260)
        for row_index, values in enumerate(rows):
            for col_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                table.setItem(row_index, col_index, item)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.resizeRowsToContents()
        content_layout.addWidget(table)
        layout.addWidget(content)

        if code == "UIX-04-A":
            approval_card, approval_layout = card()
            approval_layout.addWidget(
                muted_label(
                    "Persetujuan ini hanya menyimpan kondisi pratinjau di memori dialog. "
                    "Tidak membuat reservasi kredit dan tidak mengirim Scene."
                )
            )
            check = QCheckBox("Saya menyetujui rencana SIMULASI saja")
            check.setObjectName("UixSimulationApproval")
            approve = primary_button("Kunci Pratinjau Simulasi")
            approve.setObjectName("UixSimulationFreeze")
            approve.setEnabled(False)
            check.toggled.connect(approve.setEnabled)
            approve.clicked.connect(self._approve_preview)
            approval_layout.addWidget(check)
            approval_layout.addWidget(approve, alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(approval_card)

        actions = QHBoxLayout()
        for title, target in self._actions_for(code):
            button = QPushButton(title)
            button.setObjectName("UixAction")
            button.clicked.connect(
                lambda _checked=False, next_code=target: self.set_state(next_code)
            )
            actions.addWidget(button)
        actions.addStretch(1)
        blocked = QPushButton("Generate Live — DIBLOKIR")
        blocked.setObjectName("UixLiveGenerate")
        blocked.setToolTip(
            "G1 kebijakan, G5 kredit akun, G6 login, dan gate implementasi belum PASS."
        )
        blocked.setEnabled(False)
        actions.addWidget(blocked)
        layout.addLayout(actions)

        layout.addWidget(
            muted_label(
                "Referensi UI disetujui: 22 kondisi UIX-01..09. Angka dalam preview bukan data "
                "provider. Identitas SCENE_###, Target, model Omni Flash 1.1 • 720p • 16:9 "
                "tidak diubah oleh dialog ini."
            )
        )
        layout.addStretch(1)
        previous = self.scroller.takeWidget()
        self.scroller.setWidget(root)
        if previous is not None:
            previous.deleteLater()
        self.status.setText(f"{code} • 22 keadaan UI tersedia • hanya simulasi offline")

    def _section_title(self, code: str) -> QLabel:
        headings = {
            "01": "Scene dan kesiapan lokal",
            "02": "Alokasi profil dan estimasi fiktif",
            "03": "Asal saldo dan kelayakan kredit",
            "04": "Perubahan serta persetujuan rencana",
            "05": "Antrean dan status secara terpisah",
            "06": "Bukti rekonsiliasi (contoh, baca saja)",
            "07": "Scene terkunci dan aman untuk perencanaan ulang",
            "08": "Harga, sumber dan kebijakan",
            "09": "Generate / Download / berkas video",
        }
        label = QLabel(headings[code[4:6]])
        label.setObjectName("SectionTitle")
        return label

    def _metrics_for(self, code: str) -> list[tuple[str, str, str, str]]:
        group = code[4:6]
        count = len(self._workspace.scenes) if self._workspace is not None else 12
        demo_assigned = len(self._preview["assigned"])
        demo_blocked = len(self._preview["blocked"])
        if group == "01":
            if self._workspace is not None:
                count_ready = self._workspace.ready_count
                return [
                    ("Scene Lokal", str(count), "dari Workspace", "info"),
                    ("Siap Lokal", str(count_ready), "bukan siap Generate live", "success"),
                    (
                        "Perlu Perhatian",
                        str(self._workspace.blocking_count),
                        "input/durasi",
                        "warning",
                    ),
                    ("Kredit Provider", "—", "belum terverifikasi", "warning"),
                ]
            return [
                ("Scene contoh", "12", "data ilustrasi", "info"),
                ("Siap / perlu", "10 / 2", "skenario UIX-01-A", "success"),
                ("Profil live", "0", "tidak ada verifikasi", "warning"),
                ("Kredit provider", "—", "tidak diketahui", "warning"),
            ]
        if group in {"02", "04", "07", "08"}:
            return [
                ("Scene Contoh", "12", "data simulasi", "info"),
                ("Dialokasikan", str(demo_assigned), "perhitungan lokal", "success"),
                ("Tertahan", str(demo_blocked), "tanpa kirim ulang", "warning"),
                (
                    "Estimasi",
                    str(self._preview["total_simulated_credits"]),
                    "kredit fiktif",
                    "warning",
                ),
            ]
        if group == "03":
            return [
                ("Profil ilustrasi", "3", "bukan akun login", "info"),
                ("Saldo nyata", "—", "tidak diketahui", "warning"),
                ("Tarif terverifikasi", "Tidak", "belum ada bukti", "warning"),
                ("Live", "BLOKIR", "simulasi saja", "error"),
            ]
        if group == "05":
            return [
                ("Scene contoh", "12", "bukan progres remote", "info"),
                ("Generate asli", "0", "tidak tersambung", "warning"),
                ("Download asli", "0", "belum ada video", "warning"),
                ("Status live", "BLOKIR", "tanpa mutasi", "error"),
            ]
        if group == "06":
            return [
                ("Kasus contoh", "1", "SCENE_008", "warning"),
                ("Submit asli", "0", "tidak pernah dikirim", "info"),
                ("Remote ID nyata", "—", "tidak tersedia", "warning"),
                ("Retry otomatis", "0", "dilarang", "success"),
            ]
        return [
            ("Scene ilustrasi", "12", "bukan hasil nyata", "info"),
            ("Generated nyata", "0", "tidak ada driver live", "warning"),
            ("Downloaded nyata", "0", "tidak ada MP4 asli", "warning"),
            ("Manifest nyata", "—", "tidak dibuat di sini", "info"),
        ]

    def _data_for(self, code: str) -> tuple[list[str], list[list[str]]]:
        group = code[4:6]
        if group == "01":
            if self._workspace is not None:
                return (
                    ["Scene", "Target", "Durasi Flow", "Input", "Status Lokal"],
                    [
                        [
                            scene.scene_id,
                            f"{scene.target_duration_s:g}s",
                            str(scene.selected_flow_duration_s or "Belum dipilih"),
                            "Gambar ada" if scene.image_exists else "Gambar hilang",
                            str(scene.readiness),
                        ]
                        for scene in self._workspace.scenes
                    ],
                )
            rows = []
            for i in range(1, 13):
                name = f"SCENE_{i:03}"
                status = (
                    "GAMBAR HILANG"
                    if code == "UIX-01-B" and i == 4
                    else "PROMPT HILANG"
                    if code == "UIX-01-B" and i == 7
                    else "TARGET >10s"
                    if code == "UIX-01-B" and i == 11
                    else "PERLU REVIEW"
                    if code == "UIX-01-A" and i > 10
                    else "SIAP LOKAL"
                )
                rows.append([name, "8s" if i % 2 else "6s", "8s", "Data contoh", status])
            return ["Scene", "Target", "Flow", "Gambar/Prompt", "Kesiapan"], rows
        if group in {"02", "04", "07"}:
            rows = [
                [
                    x["scene_id"],
                    x["profile_id"],
                    f"{x['duration_s']}s",
                    f"{x['simulated_cost']} contoh",
                    "SIMULASI",
                ]
                for x in self._preview["assigned"]
            ]
            rows.extend(
                [x["scene_id"], "—", f"{x['duration_s']}s", "—", "TERTAHAN"]
                for x in self._preview["blocked"]
            )
            if code in {"UIX-07-A", "UIX-07-B"}:
                for row in rows[:4]:
                    row[-1] = "TERKUNCI (contoh)"
            return ["Scene", "Profil sintetis", "Durasi", "Kredit fiktif", "Status"], rows
        if group == "03":
            return ["Profil contoh", "Saldo ilustrasi", "Sumber", "Validitas", "Otomatisasi"], [
                [
                    "Profil A",
                    "38 (ilustrasi)",
                    "CONTOH UI",
                    "KADALUWARSA" if code.endswith("B") else "CONTOH",
                    "NONAKTIF",
                ],
                ["Profil B", "—", "INPUT MANUAL", "TIDAK TERVERIFIKASI", "NONAKTIF"],
                ["Profil C", "—", "TIDAK DIKETAHUI", "TIDAK DIKETAHUI", "NONAKTIF"],
            ]
        if group == "05":
            return ["Scene", "Profil", "Generate", "Download", "Bukti"], [
                ["SCENE_003", "Profil A", "SIMULASI antre", "Belum", "Tidak ada remote"],
                ["SCENE_006", "Profil B", "SIMULASI antre", "Belum", "Tidak ada remote"],
                ["SCENE_008", "Profil B", "TIDAK PASTI (mock)", "Belum", "Baca saja"],
                ["SCENE_009", "Profil A", "JEDA (mock)", "Belum", "Tidak ada remote"],
            ]
        if group == "06":
            return ["Kasus", "Profil", "Bukti contoh", "Tindakan aman"], [
                [
                    "SCENE_008",
                    "Profil B",
                    "ID provider: tidak tersedia",
                    "Periksa hasil (baca saja)",
                ],
                ["Login", "Profil A", "Sesi: belum diverifikasi", "Login manual"],
                ["Kredit", "Profil B", "Saldo: belum terverifikasi", "Tunda klaim baru"],
                ["Hasil (contoh)", "Profil B", "ID fiktif disamarkan", "Ke Hasil; tanpa unduh"],
            ]
        if group == "08":
            return ["Kriteria", "Sebelum", "Sekarang", "Status"], [
                ["Tarif versi", "vDEMO-1", "vDEMO-2", "SIMULASI"],
                ["Saldo provider", "—", "—", "TIDAK DIKETAHUI"],
                ["Policy otomatisasi", "—", "BELUM TERVERIFIKASI", "BLOCKED"],
                ["Model", "Omni Flash 1.1", "Omni Flash 1.1", "LOCKED"],
                ["Resolusi/aspek", "720p / 16:9", "720p / 16:9", "LOCKED"],
            ]
        return ["Scene", "Generate", "Download", "MP4 Lokal", "SHA-256"], [
            [
                f"SCENE_{i:03}",
                "CONTOH" if i <= 6 else "—",
                "CONTOH" if i <= 4 else "—",
                "TIDAK ADA",
                "—",
            ]
            for i in range(1, 13)
        ]

    def _actions_for(self, code: str) -> tuple[tuple[str, str], ...]:
        group = code[4:6]
        destinations = {
            "01": (("Tinjau Perencanaan", "UIX-02-A"), ("Lihat Masalah", "UIX-01-B")),
            "02": (("Rincian Kredit", "UIX-03-A"), ("Tinjau Anggaran", "UIX-04-A")),
            "03": (("Lihat Plan", "UIX-02-A"), ("Saldo Kadaluarsa", "UIX-03-B")),
            "04": (("Lihat Monitor", "UIX-05-A"), ("Revisi Kadaluarsa", "UIX-04-B")),
            "05": (("Periksa Ketidakpastian", "UIX-06-A"), ("Jeda Parsial", "UIX-05-B")),
            "06": (("Kembali ke Monitor", "UIX-05-A"), ("Ke Hasil", "UIX-09-A")),
            "07": (("Tinjau Rekonsiliasi", "UIX-06-A"), ("Rencana Baru", "UIX-02-A")),
            "08": (("Hitung Ulang", "UIX-02-A"), ("Alur Simulasi", "UIX-05-A")),
            "09": (("Lihat Masalah", "UIX-06-A"), ("Handoff contoh", "UIX-09-B")),
        }
        return destinations[group]

    def _approve_preview(self) -> None:
        self._last_local_plan_approved = True
        self.status.setText(
            "Simulasi dikunci secara lokal; tidak melakukan Generate atau reservasi."
        )

    def recalculate_offline(self) -> None:
        """Recalculate in memory using synthetic accounts; never call provider."""
        self._preview = simulate(_DEMO_PLAN)
        self._render(self._current_state)

    def export_preview(self) -> None:
        """Safely export a synthetic report without overwriting an existing file."""
        filename, _selected = QFileDialog.getSaveFileName(
            self, "Simpan laporan simulasi", "laporan_simulasi.json", "JSON (*.json)"
        )
        if not filename:
            return
        payload = {
            "ui_reference_state": self._current_state,
            "reference_coverage": len(UIX_SCENARIOS),
            "simulation_plan_approved_locally": self._last_local_plan_approved,
            **self._preview,
        }
        try:
            with Path(filename).open("x", encoding="utf-8") as output:
                json.dump(payload, output, indent=2, ensure_ascii=False)
                output.write("\n")
        except FileExistsError:
            QMessageBox.warning(
                self, "File sudah ada", "Laporan yang sudah ada tidak akan ditimpa."
            )
        except OSError as exc:
            QMessageBox.warning(self, "Gagal menyimpan", str(exc))
