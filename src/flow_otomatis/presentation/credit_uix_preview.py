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
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.application.ports.episode_package import EpisodeImageVerifierPort
from flow_otomatis.application.services.offline_credit_simulation import simulate
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.domain.scene import SceneReadiness
from flow_otomatis.presentation import theme
from flow_otomatis.presentation.approved_uix_assets import (
    ApprovedReferenceError,
    load_verified_reference,
)
from flow_otomatis.presentation.approved_uix_comparison import ApprovedUixComparisonDialog
from flow_otomatis.presentation.local_scene_preflight_view import LocalScenePreflightDialog
from flow_otomatis.presentation.widgets import (
    card,
    info_banner,
    metric_card,
    muted_label,
    page_header,
    primary_button,
    section_header,
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
        {"profile_id": "Profil-A", "simulated_balance": 80, "max_spend": 80},
        {"profile_id": "Profil-B", "simulated_balance": 80, "max_spend": 80},
        {"profile_id": "Profil-C", "simulated_balance": 80, "max_spend": 80},
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
    "max_total_credits": 200,
}


class CreditUixDialog(QDialog):
    """Interactive 22-state Qt preview of approved UI extension concepts."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        workspace: WorkspaceState | None = None,
        image_verifier: EpisodeImageVerifierPort | None = None,
        initial_state: str = "UIX-01-A",
        default_to_demo: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("CreditUixDialog")
        self.setWindowTitle("Flow-Otomatis | Pratinjau 22 UI Multiakun (Simulasi)")
        # Adapt the window to a 1366x768 laptop; allow Qt scroll for wide tables.
        self.setMinimumSize(1080, 600)
        screen = QApplication.primaryScreen()
        if screen is not None:
            bounds = screen.availableGeometry()
            self.resize(
                min(1720, max(1080, bounds.width() - 48)),
                min(960, max(600, bounds.height() - 48)),
            )
        else:
            self.resize(1480, 840)
        self.setStyleSheet(theme.application_stylesheet())
        self._workspace = workspace
        self._image_verifier = image_verifier
        self._preview = simulate(_DEMO_PLAN)
        self._current_state = "UIX-01-A"
        self._last_local_plan_approved = False
        self._approved_reference_folder: Path | None = None
        self._requested_scene_id: str | None = None
        self._open_scene_button: QPushButton | None = None

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
            "Beranda",
            "Workspace",
            "Hasil",
            "Profil Google",
            "Gemini Keys",
            "Diagnostik",
            "Pengaturan",
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
        top.addWidget(
            page_header("Workspace / Pratinjau Multiakun", "Omni Flash 1.1  •  720p  •  16:9")
        )
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
        dock_layout.addWidget(
            info_banner(
                "BACA SAJA",
                "Agent, login dan Generate tidak tersedia dalam pratinjau UI ini.",
                "info",
            )
        )
        dock_layout.addWidget(QLabel("KONDISI YANG DIPILIH"))
        self._dock_state = QLabel("UIX-01-A")
        self._dock_state.setObjectName("UixDockState")
        self._dock_state.setWordWrap(True)
        self._dock_state.setStyleSheet(f"font-weight: 600; color: {theme.PRIMARY};")
        dock_layout.addWidget(self._dock_state)
        dock_layout.addWidget(QLabel("RINCIAN BARIS TERPILIH"))
        self._dock_row = muted_label("Pilih baris pada tabel Workspace untuk melihat rinciannya.")
        self._dock_row.setObjectName("UixDockSelectedRow")
        self._dock_row.setMinimumHeight(86)
        dock_layout.addWidget(self._dock_row)
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

        self._source_banner = info_banner(
            "MODE SIMULASI • TIDAK TERHUBUNG GOOGLE FLOW",
            "Seluruh saldo, profil, status remote, dan biaya di panel ini adalah DATA CONTOH. "
            "Tidak ada login, Generate, Download, atau pengeluaran kredit.",
            "warning",
        )
        main.addWidget(self._source_banner)

        self.source_selector = QComboBox()
        self.source_selector.setObjectName("UixDataSourceSelector")
        self.source_selector.addItem("Skenario contoh • 12 Scene sintetis", "demo")
        if workspace is not None:
            self.source_selector.addItem("Scene Workspace lokal • baca saja", "local")
            if not default_to_demo:
                self.source_selector.setCurrentIndex(1)
            sources = QHBoxLayout()
            sources.addWidget(QLabel("Sumber data"))
            sources.addWidget(self.source_selector, 1)
            sources.addWidget(muted_label("Kredit tetap belum diverifikasi"))
            main.addLayout(sources)
        self.source_selector.currentIndexChanged.connect(self._source_changed)

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
        self.previous_state_button = QPushButton("←")
        self.previous_state_button.setObjectName("UixPreviousState")
        self.previous_state_button.setAccessibleName("Tampilan UI sebelumnya")
        self.previous_state_button.setToolTip("Tampilan UI sebelumnya")
        self.previous_state_button.clicked.connect(self._previous_state)
        navigation.addWidget(self.previous_state_button)
        self.next_state_button = QPushButton("→")
        self.next_state_button.setObjectName("UixNextState")
        self.next_state_button.setAccessibleName("Tampilan UI berikutnya")
        self.next_state_button.setToolTip("Tampilan UI berikutnya")
        self.next_state_button.clicked.connect(self._next_state)
        navigation.addWidget(self.next_state_button)
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
        self.preflight_button = QPushButton("Preflight Antrean Lokal")
        self.preflight_button.setObjectName("UixLocalPreflight")
        self.preflight_button.setToolTip(
            "Periksa kesiapan input tanpa menulis job, menghubungi provider, atau memakai kredit."
        )
        self.preflight_button.clicked.connect(self.show_local_preflight)
        self.footer.addWidget(self.preflight_button)
        # Split secondary actions into a second row for laptop-sized windows.
        secondary_actions = QHBoxLayout()
        secondary_actions.addStretch(1)
        self.export_button = QPushButton("Simpan Laporan JSON")
        self.export_button.setObjectName("UixExport")
        self.export_button.clicked.connect(self.export_preview)
        secondary_actions.addWidget(self.export_button)
        self.compare_button = QPushButton("Bandingkan UI Final")
        self.compare_button.setObjectName("UixCompareApproved")
        self.compare_button.setToolTip(
            "Tampilkan desain PNG asli yang lulus SHA-256 bersama tampilan Qt saat ini."
        )
        self.compare_button.clicked.connect(self.compare_with_approved_ui)
        secondary_actions.addWidget(self.compare_button)
        close = QPushButton("Tutup")
        close.clicked.connect(self.accept)
        secondary_actions.addWidget(close)
        main.addLayout(self.footer)
        main.addLayout(secondary_actions)
        self._group_changed(0)
        self.set_state(initial_state)

    @property
    def current_state(self) -> str:
        return self._current_state

    @property
    def requested_scene_id(self) -> str | None:
        """Selected local Scene to open in the main Workspace after dialog closes."""
        return self._requested_scene_id

    @property
    def live_dispatch_enabled(self) -> bool:
        """Fail-closed public UI guard; no real provider is ever wired here."""
        return False

    def _previous_state(self) -> None:
        index = next(i for i, item in enumerate(UIX_SCENARIOS) if item.code == self._current_state)
        self.set_state(UIX_SCENARIOS[max(0, index - 1)].code)

    def _next_state(self) -> None:
        index = next(i for i, item in enumerate(UIX_SCENARIOS) if item.code == self._current_state)
        self.set_state(UIX_SCENARIOS[min(len(UIX_SCENARIOS) - 1, index + 1)].code)

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

    def _using_local_inputs(self) -> bool:
        """True only for a persisted Workspace chosen explicitly in the data switch."""
        return self._workspace is not None and self.source_selector.currentData() == "local"

    def _source_changed(self, _index: int) -> None:
        """Switch table source without mutating persisted scenes or synthetic plan."""
        self._render(self._current_state)

    def _render(self, code: str) -> None:
        scenario = SCENARIO_BY_ID[code]
        local = self._using_local_inputs()
        mode_labels = self._source_banner.findChildren(QLabel)
        if len(mode_labels) >= 2:
            if local:
                mode_labels[0].setText("INPUT SCENE LOKAL NYATA • KREDIT TIDAK TERVERIFIKASI")
                mode_labels[1].setText(
                    "Hanya ID Scene, Target, durasi pilihan, dan kesiapan file yang berasal "
                    "dari Workspace. Tidak ada data saldo, akun, hasil Generate, atau MP4 nyata."
                )
            else:
                mode_labels[0].setText("MODE SIMULASI • TIDAK TERHUBUNG GOOGLE FLOW")
                mode_labels[1].setText(
                    "Seluruh saldo, profil, status remote, dan biaya di panel ini adalah "
                    "DATA CONTOH. Tidak ada login, Generate, Download, atau pengeluaran kredit."
                )
        self.export_button.setText("Simpan Scan Lokal JSON" if local else "Simpan Simulasi JSON")
        self.recompute_button.setEnabled(not local)
        self.preflight_button.setVisible(local)
        self.preflight_button.setEnabled(local)
        self._current_state = code
        current_index = next(i for i, item in enumerate(UIX_SCENARIOS) if item.code == code)
        self.previous_state_button.setEnabled(current_index > 0)
        self.next_state_button.setEnabled(current_index < len(UIX_SCENARIOS) - 1)
        self._dock_state.setText(f"{code} • {scenario.title}")
        self._dock_row.setText("Pilih baris pada tabel Workspace untuk melihat rinciannya.")
        self._last_local_plan_approved = False
        self._open_scene_button = None
        root = QWidget()
        root.setObjectName(f"UixPage{code.replace('-', '')}")
        page_layout = QVBoxLayout(root)
        page_layout.setContentsMargins(10, 4, 10, 12)
        page_layout.setSpacing(12)
        if not local and code[4:6] in {"02", "04", "07", "08"}:
            # Approved groups use temporary centered planning/approval/policy
            # dialogs; keep the seven frozen app routes unchanged behind them.
            modal = QFrame(root)
            modal.setObjectName("UixScenarioModal")
            modal.setMaximumWidth(1120)
            modal.setStyleSheet(
                f"QFrame#UixScenarioModal {{ background: white; "
                f"border: 1px solid {theme.BORDER}; border-radius: 10px; }}"
            )
            layout = QVBoxLayout(modal)
            layout.setContentsMargins(22, 18, 22, 20)
            layout.setSpacing(12)
            page_layout.addWidget(modal, alignment=Qt.AlignmentFlag.AlignHCenter)
            page_layout.addStretch(1)
        else:
            layout = page_layout
        layout.addWidget(page_header(f"{scenario.code} · {scenario.title}", scenario.description))
        if local:
            layout.addWidget(
                info_banner(
                    "PEMERIKSAAN INPUT WORKSPACE • BUKAN STATUS GOOGLE FLOW",
                    "Hasil alokasi, saldo, recovery, dan tarif pada contoh UIX ini bukan "
                    "hasil proyek Anda. Alihkan sumber data ke Skenario Contoh untuk "
                    "mempelajari masing-masing keadaan UI.",
                    "info",
                )
            )
        else:
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
        finder = QHBoxLayout()
        search = QLineEdit()
        search.setObjectName("UixTableSearch")
        search.setClearButtonEnabled(True)
        search.setPlaceholderText(
            "Cari ID Scene atau input lokal..."
            if local
            else "Cari Scene, profil, status, atau bukti..."
        )
        search.setAccessibleName("Cari data dalam tabel pratinjau")
        finder.addWidget(search, 1)
        readiness_filter = QComboBox()
        readiness_filter.setObjectName("UixReadinessFilter")
        if local:
            readiness_filter.addItem("Semua kesiapan", None)
            readiness_filter.addItem("Perlu diperbaiki", "PROBLEM")
            readiness_filter.addItem("Perlu pilih durasi", "PILIH DURASI")
            readiness_filter.addItem("Siap lokal", "SIAP LOKAL")
            readiness_filter.addItem("Gambar hilang", "GAMBAR HILANG")
            readiness_filter.addItem("Prompt hilang", "PROMPT HILANG")
            readiness_filter.addItem("Durasi invalid", "DURASI INVALID")
            finder.addWidget(readiness_filter)
        matches = muted_label(f"{len(rows)} baris ({'lokal' if local else 'contoh'})")
        matches.setObjectName("UixFilterCount")
        finder.addWidget(matches)
        content_layout.addLayout(finder)
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
        # Horizontal scrolling preserves readable IDs, titles and status columns.
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        for column in range(len(columns)):
            suggested = table.sizeHintForColumn(column) + 22
            table.setColumnWidth(column, min(260, max(112, suggested)))
        table.resizeRowsToContents()
        table.itemSelectionChanged.connect(lambda view=table: self._selected_row_details(view))

        def refresh_filtered_rows() -> None:
            self._filter_rows(
                table,
                matches,
                search.text(),
                local,
                readiness_filter.currentData() if local else None,
            )

        search.textChanged.connect(lambda _query: refresh_filtered_rows())
        if local:
            readiness_filter.currentIndexChanged.connect(lambda _index: refresh_filtered_rows())
        if rows:
            table.setCurrentCell(0, 0)
        content_layout.addWidget(table)
        if not local and code in {"UIX-02-A", "UIX-08-A", "UIX-08-B"}:
            # Original approved screenshots have two columns in the modal.
            content.setMinimumWidth(420)
            two_columns = QHBoxLayout()
            two_columns.setSpacing(12)
            two_columns.addWidget(content, 3)
            two_columns.addWidget(self._scenario_detail_panel(code), 2)
            layout.addLayout(two_columns)
        else:
            layout.addWidget(content)

        if code == "UIX-04-A" and not local:
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
        if local:
            open_scene = primary_button("Buka Scene Terpilih di Workspace")
            open_scene.setObjectName("UixOpenSceneInWorkspace")
            open_scene.setEnabled(False)
            open_scene.clicked.connect(
                lambda _checked=False, view=table: self._request_open_scene(view)
            )
            self._open_scene_button = open_scene
            actions.addWidget(open_scene)
            self._selected_row_details(table)
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
        self.status.setText(
            f"{code} • {'scan input lokal baca saja' if local else 'simulasi 12 Scene offline'} "
            "• Generate live diblokir"
        )

    def _selected_row_details(self, table: QTableWidget) -> None:
        """Read-only inspector and safe local navigation state for the visible row."""
        index = table.currentRow()
        valid_row = index >= 0 and not table.isRowHidden(index)
        if self._open_scene_button is not None:
            self._open_scene_button.setEnabled(
                valid_row and self._valid_scene_id(table, index) is not None
            )
        if not valid_row:
            self._dock_row.setText("Tidak ada baris yang dipilih.")
            return
        values: list[str] = []
        for column in range(table.columnCount()):
            header = table.horizontalHeaderItem(column)
            item = table.item(index, column)
            title = header.text() if header is not None else f"Kolom {column + 1}"
            value = item.text() if item is not None else "—"
            values.append(f"{title}: {value}")
        self._dock_row.setText("\n".join(values))

    def _filter_rows(
        self,
        table: QTableWidget,
        count_label: QLabel,
        query: str,
        is_local: bool = False,
        readiness: str | None = None,
    ) -> None:
        """Filter only visible synthetic/local table data without changing totals."""
        needle = query.strip().casefold()
        visible = 0
        for row_index in range(table.rowCount()):
            values: list[str] = []
            for col in range(table.columnCount()):
                item = table.item(row_index, col)
                if item is not None:
                    values.append(item.text())
            found = any(needle in text.casefold() for text in values)
            if is_local and readiness:
                status = values[-1] if values else ""
                if readiness == "PROBLEM":
                    found = found and status in {
                        "GAMBAR HILANG",
                        "PROMPT HILANG",
                        "DURASI INVALID",
                    }
                else:
                    found = found and status == readiness
            table.setRowHidden(row_index, not found)
            visible += int(found)
        count_label.setText(
            f"{visible}/{table.rowCount()} baris ({'lokal' if is_local else 'contoh'})"
        )
        current = table.currentRow()
        if current < 0 or table.isRowHidden(current):
            replacement = next(
                (row for row in range(table.rowCount()) if not table.isRowHidden(row)),
                -1,
            )
            if replacement < 0:
                table.clearSelection()
                self._dock_row.setText("Tidak ada baris yang cocok dengan pencarian.")
            else:
                table.setCurrentCell(replacement, 0)
        else:
            self._selected_row_details(table)
        if visible == 0 and self._open_scene_button is not None:
            self._open_scene_button.setEnabled(False)

    def _valid_scene_id(self, table: QTableWidget, row: int) -> str | None:
        """Only a real persisted Scene can be handed back to the main Workspace."""
        if not self._using_local_inputs() or self._workspace is None or row < 0:
            return None
        item = table.item(row, 0)
        if item is None or table.isRowHidden(row):
            return None
        candidate = item.text()
        return (
            candidate
            if any(scene.scene_id == candidate for scene in self._workspace.scenes)
            else None
        )

    def _request_open_scene(self, table: QTableWidget) -> None:
        target = self._valid_scene_id(table, table.currentRow())
        if target is None:
            return
        self._requested_scene_id = target
        self.accept()

    def _scenario_detail_panel(self, code: str) -> QWidget:
        """Render approved UIX-02/08 right-hand content in Qt; synthetic only."""

        titles = {
            "UIX-02-A": "Distribusi per Profil",
            "UIX-08-A": "Dampak pada Rencana",
            "UIX-08-B": "Dampak pada Proyek",
        }
        rows: dict[str, tuple[tuple[str, str], ...]] = {
            "UIX-02-A": (
                ("Profil A • contoh", "4 scene"),
                ("Profil B • contoh", "4 scene"),
                ("Profil C • contoh", "2 scene"),
                ("Belum dialokasikan", "2 scene"),
            ),
            "UIX-08-A": (
                ("Rencana sebelumnya", "v3 • TIDAK BERLAKU"),
                ("Tarif lama", "vDEMO-1 • kadaluarsa"),
                ("Tarif baru", "vDEMO-2 • belum dicek"),
                ("Estimasi baru", "BELUM TERSEDIA"),
                ("Hitung ulang / Generate", "DINONAKTIFKAN"),
            ),
            "UIX-08-B": (
                ("Scene siap • contoh", "10 scene"),
                ("Perlu perhatian • contoh", "2 scene"),
                ("Bukti izin multiakun", "BELUM ADA"),
                ("Saldo live terverifikasi", "—"),
                ("Tarif resmi", "TIDAK DIKETAHUI"),
                ("Mulai Batch / Generate", "DINONAKTIFKAN"),
            ),
        }
        panel, body = card(9)
        panel.setObjectName("UixScenarioSidePanel")
        body.addWidget(section_header(titles[code]))
        body.addWidget(muted_label("Data simulasi; bukan bukti dari Google Flow."))
        for label, value in rows[code]:
            line = QWidget()
            line_layout = QHBoxLayout(line)
            line_layout.setContentsMargins(1, 5, 1, 5)
            line_layout.setSpacing(8)
            line_layout.addWidget(muted_label(label), 2)
            result = QLabel(value)
            result.setObjectName("UixScenarioDetailValue")
            result.setWordWrap(True)
            line_layout.addWidget(result, 2)
            body.addWidget(line)
        body.addWidget(
            info_banner(
                "AKSI LIVE TIDAK TERSEDIA",
                "Periksa tarif, kredit, identitas dan kebijakan sebelum Generate.",
                "warning",
            )
        )
        body.addStretch(1)
        return panel

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
        label = QLabel(
            "Kesiapan input Scene Workspace nyata • hanya baca"
            if self._using_local_inputs()
            else headings[code[4:6]]
        )
        label.setObjectName("SectionTitle")
        return label

    def _metrics_for(self, code: str) -> list[tuple[str, str, str, str]]:
        group = code[4:6]
        if self._using_local_inputs():
            workspace = self._workspace
            assert workspace is not None
            return [
                ("Scene Lokal", str(len(workspace.scenes)), "input tersimpan", "info"),
                ("Siap Lokal", str(workspace.ready_count), "belum siap live", "success"),
                (
                    "Pilih Durasi",
                    str(workspace.duration_selection_count),
                    "butuh pilihan user",
                    "warning",
                ),
                ("Input Bermasalah", str(workspace.blocking_count), "cek gambar/prompt", "error"),
            ]
        demo_assigned = len(self._preview["assigned"])
        demo_blocked = len(self._preview["blocked"])
        if code == "UIX-01-B":
            return [
                ("Scene Contoh", "12", "data ilustrasi", "info"),
                ("Siap Lokal", "9", "contoh 9 siap", "success"),
                ("Perlu Perhatian", "3", "gambar/prompt/Target", "warning"),
                ("Kredit Nyata", "—", "tidak diketahui", "warning"),
            ]
        if code == "UIX-01-C":
            return [
                ("Scene contoh", "12", "input lokal valid", "info"),
                ("Tarif Provider", "—", "belum terverifikasi", "warning"),
                ("Saldo Provider", "—", "tidak diketahui", "warning"),
                ("Live", "BLOKIR", "bukan saldo nol", "error"),
            ]
        if group == "01":
            return [
                ("Scene contoh", "12", "data ilustrasi", "info"),
                ("Siap / perlu", "10 / 2", "skenario UIX-01-A", "success"),
                ("Profil live", "0", "tidak ada verifikasi", "warning"),
                ("Kredit provider", "—", "tidak diketahui", "warning"),
            ]
        if code == "UIX-08-A":
            return [
                ("Tarif Lama", "vDEMO-1", "versi fiktif", "warning"),
                ("Tarif Baru", "vDEMO-2", "perlu verifikasi", "warning"),
                ("Rencana Lama", "KADALUARSA", "tidak boleh digunakan", "error"),
                ("Persetujuan", "ULANG", "harus dihitung kembali", "error"),
            ]
        if code == "UIX-08-B":
            return [
                ("Izin Provider", "BELUM ADA", "tidak terverifikasi", "error"),
                ("Multiakun Live", "DIBLOKIR", "tanpa pengecualian", "error"),
                ("Saldo Terbukti", "—", "tidak diketahui", "warning"),
                ("Generate", "NONAKTIF", "tidak melakukan submit", "error"),
            ]
        if code == "UIX-02-A":
            return [
                ("Scene Contoh", "12", "data fiktif", "info"),
                ("Terbagi", str(demo_assigned), "simulasi lokal", "success"),
                ("Ditahan", str(demo_blocked), "simulasi lokal", "warning"),
                ("Persetujuan", "BELUM", "hanya plan, bukan izin", "warning"),
            ]
        if code == "UIX-02-B":
            return [
                ("Scene contoh", "12", "data simulasi", "info"),
                ("Terbagi", "8", "contoh subset", "success"),
                ("Tertahan", "4", "anggaran contoh", "warning"),
                ("Generate Live", "BLOKIR", "tanpa izin provider", "error"),
            ]
        if code == "UIX-02-C":
            return [
                ("Scene contoh", "12", "data simulasi", "info"),
                ("Akun layak nyata", "0", "tidak diverifikasi", "warning"),
                ("Belum dialokasikan", "12", "tidak ada akun layak", "error"),
                ("Generate Live", "BLOKIR", "periksa kebijakan", "error"),
            ]
        if code == "UIX-03-A":
            return [
                ("Saldo ilustrasi", "38", "bukan angka aktual", "info"),
                ("Reservasi contoh", "12", "hanya ilustrasi", "warning"),
                ("Tersedia contoh", "26", "tidak bisa digunakan", "info"),
                ("Saldo live", "—", "tidak diverifikasi", "warning"),
            ]
        if code == "UIX-05-B":
            return [
                ("Generated contoh", "5", "bukan remote", "info"),
                ("Await download", "2", "contoh terpisah", "warning"),
                ("Antre", "3", "tidak dikirim", "info"),
                ("Perhatian", "2", "jangan retry", "error"),
            ]
        if code == "UIX-05-C":
            return [
                ("Kasus contoh", "SCENE_008", "Profil B saja", "warning"),
                ("Submit", "UNCERTAIN", "tidak boleh retry", "error"),
                ("Cadangan", "HELD", "contoh, bukan debit", "warning"),
                ("Profil A", "MANDIRI", "tidak dipindah", "success"),
            ]
        if code == "UIX-09-A":
            return [
                ("Generated contoh", "6", "tidak ada video nyata", "info"),
                ("Downloaded contoh", "4", "tidak ada MP4 nyata", "warning"),
                ("Perlu perhatian", "2", "data ilustrasi", "warning"),
                ("Checksum aktual", "—", "tidak tersedia", "warning"),
            ]
        if code == "UIX-09-B":
            return [
                ("Scene contoh", "12/12", "hanya ilustrasi", "info"),
                ("Video MP4 nyata", "0", "tidak ada file", "warning"),
                ("Manifest nyata", "—", "belum dibuat", "info"),
                ("Klaim selesai", "TIDAK", "contoh saja", "success"),
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
        if self._using_local_inputs():
            workspace = self._workspace
            assert workspace is not None
            ready_labels = {
                SceneReadiness.READY: "SIAP LOKAL",
                SceneReadiness.NEEDS_DURATION_SELECTION: "PILIH DURASI",
                SceneReadiness.MISSING_IMAGE: "GAMBAR HILANG",
                SceneReadiness.MISSING_PROMPT: "PROMPT HILANG",
                SceneReadiness.INVALID_DURATION: "DURASI INVALID",
            }
            return (
                ["Scene", "Target", "Durasi Flow", "Gambar", "Prompt", "Kesiapan Lokal"],
                [
                    [
                        scene.scene_id,
                        f"{scene.target_duration_s:.2f}s",
                        (
                            f"{scene.selected_flow_duration_s}s"
                            if scene.selected_flow_duration_s is not None
                            else f"Belum dipilih • saran {scene.recommended_flow_duration_s}s"
                        ),
                        "ADA" if scene.image_exists else "HILANG",
                        "ADA" if scene.motion_prompt.strip() else "HILANG",
                        ready_labels[scene.readiness],
                    ]
                    for scene in workspace.scenes
                ],
            )
        # UIX variants are different state machines, not 22 captions pasted on
        # one successful allocation table. Keep every value explicitly synthetic.
        if code in {"UIX-02-B", "UIX-02-C"}:
            columns = ["Scene", "Profil simulasi", "Durasi", "Estimasi fiktif", "Status"]
            if code == "UIX-02-C":
                return columns, [
                    [f"SCENE_{index:03}", "—", "—", "—", "TIDAK ADA AKUN LAYAK"]
                    for index in range(1, 13)
                ]
            subset = [
                [
                    row["scene_id"],
                    row["profile_id"],
                    f"{row['duration_s']}s",
                    str(row["simulated_cost"]),
                    "SIMULASI",
                ]
                for row in self._preview["assigned"][:8]
            ]
            subset.extend(
                [f"SCENE_{index:03}", "—", "—", "—", "BELUM DIALOKASIKAN"] for index in range(9, 13)
            )
            return columns, subset
        if code == "UIX-08-A":
            return ["Dasar Rencana", "Versi Lama", "Versi Baru", "Keputusan"], [
                ["Tarif model", "vDEMO-1", "vDEMO-2", "HITUNG ULANG"],
                ["Estimasi 12 Scene", "Tidak berlaku", "Belum dihitung", "TUNDA"],
                ["Kredit nyata", "Tidak diketahui", "Tidak diketahui", "VERIFIKASI"],
                ["Persetujuan rencana", "KADALUARSA", "BELUM", "MINTA ULANG"],
                ["Generate / Download", "BELUM", "NONAKTIF", "DIBLOKIR"],
            ]
        if code == "UIX-08-B":
            return ["Persyaratan", "Bukti", "Status", "Tindakan Aman"], [
                [
                    "G1 • Izin otomatisasi",
                    "Tidak tersedia",
                    "BELUM TERVERIFIKASI",
                    "JANGAN GENERATE",
                ],
                ["G1 • Izin multiakun", "Tidak tersedia", "BELUM TERVERIFIKASI", "JANGAN ROTASI"],
                ["G5 • Tarif dan saldo", "Tidak tersedia", "TIDAK DIKETAHUI", "TUNDA KREDIT"],
                ["G6 • READY pasca-restart", "Tidak tersedia", "BELUM LULUS", "CEK MANUAL"],
                ["Persetujuan rencana", "Hanya simulasi", "TIDAK BERLAKU LIVE", "JANGAN SUBMIT"],
            ]
        if code == "UIX-04-B":
            return ["Perubahan contoh", "Sebelum", "Sesudah", "Dampak"], [
                ["SCENE_006 • gambar", "Revisi v3", "Gambar berubah", "WAJIB REPLAN"],
                ["Tarif simulasi", "vDEMO-1", "vDEMO-2", "HITUNG ULANG"],
                ["Bukti kredit nyata", "—", "Belum diverifikasi", "LIVE BLOKIR"],
            ]
        if code == "UIX-05-B":
            rows = []
            for index in range(1, 13):
                if index <= 5:
                    stage = "GENERATED (contoh)"
                elif index <= 7:
                    stage = "AWAIT DOWNLOAD (contoh)"
                elif index <= 10:
                    stage = "ANTRE (contoh)"
                else:
                    stage = "PERLU PERHATIAN"
                rows.append(
                    [
                        f"SCENE_{index:03}",
                        "Profil A/B (contoh)",
                        stage,
                        "Belum",
                        "Tidak ada bukti provider",
                    ]
                )
            return ["Scene", "Profil", "Status", "Download", "Bukti"], rows
        if code == "UIX-05-C":
            return ["Scene", "Profil simulasi", "Kondisi", "Kredit", "Tindakan"], [
                ["SCENE_008", "Profil B", "SUBMIT_UNCERTAIN", "HELD (contoh)", "Baca saja"],
                ["SCENE_003", "Profil A", "MANDIRI (contoh)", "—", "Tetap terpisah"],
            ]
        if code == "UIX-06-C":
            return ["Kasus", "Bukti ilustrasi", "Generate", "Download"], [
                ["SCENE_008", "ID DEMO tertaut Profil B", "Ditemukan (contoh)", "BELUM"],
                ["Riwayat", "Rekonsiliasi baca saja", "Tidak ada submit baru", "BELUM"],
            ]
        if code == "UIX-07-B":
            rows = []
            for index in range(1, 13):
                scene_id = f"SCENE_{index:03}"
                if index == 3:
                    status = "TERKUNCI • SUBMIT_UNCERTAIN"
                    profile = "Profil B (contoh)"
                elif index <= 4:
                    status = "TERKUNCI (contoh)"
                    profile = "Tidak dapat dipindah"
                else:
                    status = "AMAN UNTUK REPLAN (contoh)"
                    profile = "Belum dibekukan"
                rows.append([scene_id, profile, status, "Tanpa live dispatch"])
            return ["Scene", "Profil", "Kondisi", "Tindakan aman"], rows
        if code in {"UIX-09-A", "UIX-09-B"}:
            rows = []
            for index in range(1, 13):
                if code == "UIX-09-B":
                    generated = downloaded = "12/12 CONTOH"
                else:
                    generated = "CONTOH" if index <= 6 else "—"
                    downloaded = "CONTOH" if index <= 4 else "—"
                rows.append(
                    [f"SCENE_{index:03}", generated, downloaded, "TIDAK ADA MP4 NYATA", "—"]
                )
            return ["Scene", "Generate", "Download", "File lokal", "SHA-256"], rows
        group = code[4:6]
        if group == "01":
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
        """Show state-specific review routes, never a simulated live submission."""
        if self._using_local_inputs():
            return (("Tinjau Scene Lokal", "UIX-01-A"), ("Masalah Input Lokal", "UIX-01-B"))
        destinations: dict[str, tuple[tuple[str, str], ...]] = {
            "UIX-01-A": (("Tinjau Perencanaan", "UIX-02-A"), ("Lihat Masalah", "UIX-01-B")),
            "UIX-01-B": (("Periksa Scan", "UIX-01-A"), ("Periksa Kredit", "UIX-01-C")),
            "UIX-01-C": (("Rincian Kredit", "UIX-03-B"), ("Alur Manual", "UIX-08-B")),
            "UIX-02-A": (("Rincian Kredit", "UIX-03-A"), ("Tinjau Approval", "UIX-04-A")),
            "UIX-02-B": (("Tinjau Subset", "UIX-07-A"), ("Periksa Profil", "UIX-03-B")),
            "UIX-02-C": (("Periksa Profil", "UIX-03-B"), ("Baca Persyaratan", "UIX-08-B")),
            "UIX-03-A": (("Tinjau Rencana", "UIX-02-A"), ("Saldo Kadaluarsa", "UIX-03-B")),
            "UIX-03-B": (("Sumber Kredit", "UIX-08-B"), ("Akun Tidak Layak", "UIX-02-C")),
            "UIX-04-A": (("Monitor Contoh", "UIX-05-A"), ("Plan Kadaluarsa", "UIX-04-B")),
            "UIX-04-B": (("Hitung Ulang", "UIX-02-A"), ("Lihat Perubahan", "UIX-08-A")),
            "UIX-05-A": (("Jeda Parsial", "UIX-05-B"), ("Submit Uncertain", "UIX-05-C")),
            "UIX-05-B": (("Periksa Hasil", "UIX-09-A"), ("Kembali Monitor", "UIX-05-A")),
            "UIX-05-C": (("Tinjau Bukti", "UIX-06-A"), ("Jeda Profil B", "UIX-06-B")),
            "UIX-06-A": (("Konflik Akun", "UIX-06-B"), ("Hasil Contoh", "UIX-06-C")),
            "UIX-06-B": (("Monitor Profil", "UIX-05-C"), ("Periksa Kredit", "UIX-03-B")),
            "UIX-06-C": (("Ke Hasil", "UIX-09-A"), ("Kembali Monitor", "UIX-05-A")),
            "UIX-07-A": (("Scene Terkunci", "UIX-07-B"), ("Rencana Baru", "UIX-02-A")),
            "UIX-07-B": (("Lihat Rekonsiliasi", "UIX-06-A"), ("Kembali Replan", "UIX-07-A")),
            "UIX-08-A": (("Hitung Ulang", "UIX-02-A"), ("Baca Kebijakan", "UIX-08-B")),
            "UIX-08-B": (("Gunakan Simulasi", "UIX-02-A"), ("Periksa Sumber", "UIX-03-B")),
            "UIX-09-A": (("Handoff Contoh", "UIX-09-B"), ("Lihat Masalah", "UIX-06-A")),
            "UIX-09-B": (("Hasil Parsial", "UIX-09-A"), ("Kembali Workspace", "UIX-01-A")),
        }
        return destinations[code]

    def _approve_preview(self) -> None:
        self._last_local_plan_approved = True
        self.status.setText(
            "Simulasi dikunci secara lokal; tidak melakukan Generate atau reservasi."
        )

    def recalculate_offline(self) -> None:
        """Recalculate in memory using synthetic accounts; never call provider."""
        self._preview = simulate(_DEMO_PLAN)
        self._render(self._current_state)

    def show_local_preflight(self) -> None:
        """Compute a read-only preview, never enqueue or start a real job."""
        if not self._using_local_inputs() or self._workspace is None:
            return
        preview = LocalScenePreflightDialog(
            self._workspace, parent=self, image_verifier=self._image_verifier
        )
        preview.exec()
        if preview.requested_scene_id is not None:
            self._requested_scene_id = preview.requested_scene_id
            self.accept()

    def compare_with_approved_ui(self) -> None:
        """Inspect frozen UI image next to Qt; never alter the reference file."""
        try:
            approved_image = load_verified_reference(
                self._current_state,
                supplied_directory=self._approved_reference_folder,
            )
        except ApprovedReferenceError:
            # Main portable can use the original reference folder manually;
            # the standalone preview EXE embeds all 22 PNG files at build time.
            selected = QFileDialog.getExistingDirectory(
                self,
                "Pilih folder 22 PNG UI final yang telah disetujui",
                "",
            )
            if not selected:
                return
            try:
                approved_image = load_verified_reference(
                    self._current_state,
                    supplied_directory=Path(selected),
                )
            except (ApprovedReferenceError, OSError) as exc:
                QMessageBox.warning(self, "Referensi tidak cocok", str(exc))
                return
            self._approved_reference_folder = Path(selected)
        except OSError as exc:
            QMessageBox.warning(self, "Referensi tidak dapat dibaca", str(exc))
            return

        current_view = self.grab()
        dialog = ApprovedUixComparisonDialog(
            self._current_state,
            approved_image,
            current_view,
            parent=self,
        )
        dialog.exec()

    def _report_payload(self) -> dict[str, Any]:
        """Separate local readiness evidence from wholly fictional credit reports."""
        if self._using_local_inputs():
            workspace = self._workspace
            assert workspace is not None
            return {
                "mode": "LOCAL_SCENE_READINESS_REPORT",
                "provider_evidence": "NONE",
                "live_dispatch_allowed": False,
                "ui_reference_state": self._current_state,
                "episode_id": workspace.episode_id,
                "project_name": workspace.project_name,
                "scene_count": len(workspace.scenes),
                "ready_count": workspace.ready_count,
                "needs_duration_selection": workspace.duration_selection_count,
                "blocking_count": workspace.blocking_count,
                "scenes": [
                    {
                        "scene_id": scene.scene_id,
                        "target_duration_s": scene.target_duration_s,
                        "recommended_flow_duration_s": scene.recommended_flow_duration_s,
                        "selected_flow_duration_s": scene.selected_flow_duration_s,
                        "image_exists": scene.image_exists,
                        "prompt_present": bool(scene.motion_prompt.strip()),
                        "readiness": str(scene.readiness),
                    }
                    for scene in workspace.scenes
                ],
            }
        return {
            "ui_reference_state": self._current_state,
            "reference_coverage": len(UIX_SCENARIOS),
            "simulation_plan_approved_locally": self._last_local_plan_approved,
            **self._preview,
        }

    def export_preview(self) -> None:
        """Export one clearly labeled mode using exclusive creation (no overwrite)."""
        local = self._using_local_inputs()
        filename, _selected = QFileDialog.getSaveFileName(
            self,
            "Simpan scan lokal" if local else "Simpan laporan simulasi",
            "scan_scene_lokal.json" if local else "laporan_simulasi.json",
            "JSON (*.json)",
        )
        if not filename:
            return
        payload = self._report_payload()
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
