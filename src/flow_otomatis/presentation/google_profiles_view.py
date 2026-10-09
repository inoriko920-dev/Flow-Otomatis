"""Real authorized Google profile/session views using frozen STEP 09 composition."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import UTC

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from flow_otomatis.application.ports.google_flow_preflight import (
    GoogleFlowAccessProbe,
    GoogleFlowAccessState,
)
from flow_otomatis.application.ports.google_session import (
    GoogleSessionProfile,
    GoogleSessionRestartGate,
    GoogleSessionState,
)
from flow_otomatis.presentation.widgets import (
    card,
    info_banner,
    labeled_value,
    page_header,
    primary_button,
    secondary_button,
    section_header,
    table_widget,
)

_FLOW_TEXT = {
    GoogleFlowAccessState.REACHABLE_ONLY: "Halaman terjangkau; akses belum terverifikasi",
    GoogleFlowAccessState.AUTH_REQUIRED: "Perlu login Google",
    GoogleFlowAccessState.UNAVAILABLE: "Flow belum tersedia",
    GoogleFlowAccessState.UNKNOWN: "Belum dapat dipastikan",
    GoogleFlowAccessState.ERROR: "Gagal diperiksa",
    GoogleFlowAccessState.ACCESS_VERIFIED: "Akses terverifikasi",
    GoogleFlowAccessState.UNCHECKED: "Belum diperiksa",
    GoogleFlowAccessState.CHECKING: "Sedang diperiksa",
}

_STATE_TEXT = {
    GoogleSessionState.READY: "Siap",
    GoogleSessionState.NEEDS_LOGIN: "Perlu Login",
    GoogleSessionState.UNKNOWN: "Belum pasti",
    GoogleSessionState.ERROR: "Perhatian",
}


def _last_checked(profile: GoogleSessionProfile) -> str:
    checked = profile.last_checked_at
    if checked is None:
        return "—"
    if checked.tzinfo is None:
        checked = checked.replace(tzinfo=UTC)
    return checked.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def build_google_profiles_view(
    profiles: Sequence[GoogleSessionProfile],
    *,
    on_add: Callable[[], None],
    on_check_all: Callable[[], None],
    on_open_login: Callable[[str], None],
    on_check: Callable[[str], None],
) -> QWidget:
    """Render real safe profile metadata without exposing browser-session secrets."""

    root = QWidget()
    layout = QVBoxLayout(root)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(12)
    layout.addWidget(
        page_header("Profil Google", "Kelola sesi Google yang Anda otorisasi secara manual")
    )

    toolbar = QWidget()
    toolbar_layout = QHBoxLayout(toolbar)
    toolbar_layout.setContentsMargins(0, 0, 0, 0)
    add_button = primary_button("Tambah Profil")
    check_all_button = secondary_button("Cek Semua Sesi")
    add_button.clicked.connect(lambda checked=False: on_add())
    check_all_button.clicked.connect(lambda checked=False: on_check_all())
    toolbar_layout.addWidget(add_button)
    toolbar_layout.addWidget(check_all_button)
    toolbar_layout.addStretch(1)
    layout.addWidget(toolbar)

    if not profiles:
        layout.addWidget(
            info_banner(
                "Belum ada profil Google",
                "Tambahkan profil lalu selesaikan login secara manual pada halaman resmi Google.",
                "info",
            )
        )
        layout.addStretch(1)
        return root

    rows = [
        [
            profile.label,
            _STATE_TEXT[profile.state],
            "Tersedia" if profile.state is GoogleSessionState.READY else "Tidak tersedia",
            _last_checked(profile),
            profile.detail,
        ]
        for profile in profiles
    ]
    table = table_widget(
        ["Profil", "Status", "Ketersediaan", "Cek terakhir", "Catatan"],
        rows,
        stretch_column=4,
    )
    table.setObjectName("GoogleProfilesTable")
    table.setCurrentCell(0, 0)
    layout.addWidget(table, 1)

    actions = QWidget()
    actions_layout = QHBoxLayout(actions)
    actions_layout.setContentsMargins(0, 0, 0, 0)
    open_button = primary_button("Buka / Fokuskan Sesi Login")
    check_button = secondary_button("Cek Ulang Sesi")

    def selected_profile_id() -> str | None:
        row = table.currentRow()
        if row < 0 or row >= len(profiles):
            return None
        return profiles[row].profile_id

    def open_selected() -> None:
        profile_id = selected_profile_id()
        if profile_id is not None:
            on_open_login(profile_id)

    def check_selected() -> None:
        profile_id = selected_profile_id()
        if profile_id is not None:
            on_check(profile_id)

    open_button.clicked.connect(lambda checked=False: open_selected())
    check_button.clicked.connect(lambda checked=False: check_selected())
    actions_layout.addStretch(1)
    actions_layout.addWidget(check_button)
    actions_layout.addWidget(open_button)
    layout.addWidget(actions)
    return root


def build_google_login_view(
    profile: GoogleSessionProfile,
    *,
    restart_gate: GoogleSessionRestartGate,
    on_open_login: Callable[[], None],
    on_recheck: Callable[[], None],
    on_back: Callable[[], None],
    flow_probe: GoogleFlowAccessProbe | None = None,
    flow_busy: bool = False,
    on_check_flow: Callable[[], None] | None = None,
) -> QWidget:
    """Render real manual-login help/status for one safe profile."""

    root = QWidget()
    layout = QVBoxLayout(root)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(12)
    layout.addWidget(page_header("Bantuan Login", profile.label))

    if profile.state is GoogleSessionState.READY:
        layout.addWidget(
            info_banner(
                "Sesi berhasil diverifikasi",
                f"{profile.label} sekarang siap digunakan.",
                "success",
            )
        )
        if restart_gate.ready_after_restart:
            layout.addWidget(
                info_banner(
                    "Restart berhasil diverifikasi",
                    "Sesi tetap Siap setelah aplikasi ditutup dan dibuka kembali.",
                    "success",
                )
            )
        else:
            layout.addWidget(
                info_banner(
                    "Restart belum diverifikasi",
                    "Sesi sudah Siap, tetapi belum terbukti bertahan setelah restart aplikasi.",
                    "info",
                )
            )
    elif profile.state is GoogleSessionState.ERROR:
        layout.addWidget(info_banner("Sesi memerlukan perhatian", profile.detail, "error"))
    elif profile.state is GoogleSessionState.UNKNOWN:
        layout.addWidget(info_banner("Perlu verifikasi ulang", profile.detail, "info"))
    else:
        layout.addWidget(
            info_banner(
                "Login manual diperlukan",
                "Aplikasi tidak mengisi password, MFA, atau CAPTCHA. "
                "Selesaikan sendiri pada halaman resmi Google.",
                "warning",
            )
        )

    steps, steps_layout = card(8)
    steps_layout.addWidget(section_header("Langkah aman"))
    steps_layout.addWidget(labeled_value("Profil", profile.label, strong=True))
    steps_layout.addWidget(labeled_value("Status", _STATE_TEXT[profile.state]))
    steps_layout.addWidget(
        labeled_value(
            "Validasi restart",
            "Lulus" if restart_gate.ready_after_restart else "Belum lulus",
            strong=restart_gate.ready_after_restart,
        )
    )
    flow_status = (
        "Sedang diperiksa"
        if flow_busy
        else _FLOW_TEXT[flow_probe.state]
        if flow_probe is not None
        else "Belum diperiksa"
    )
    steps_layout.addWidget(labeled_value("Akses Flow", flow_status))
    if flow_probe is not None:
        steps_layout.addWidget(
            info_banner(
                "Hasil pemeriksaan Flow (hanya-baca)",
                flow_probe.detail,
                "info",
            )
        )
    steps_layout.addWidget(labeled_value("1", "Buka sesi login di Google Chrome normal"))
    steps_layout.addWidget(labeled_value("2", "Selesaikan login, MFA, atau CAPTCHA secara manual"))
    steps_layout.addWidget(
        labeled_value("3", "Setelah login berhasil, tutup jendela Google Chrome login")
    )
    steps_layout.addWidget(labeled_value("4", "Kembali lalu pilih Cek Ulang Sesi"))
    steps_layout.addWidget(
        labeled_value(
            "5",
            "Setelah status Siap, tutup aplikasi, buka kembali, lalu Cek Ulang Sesi lagi.",
        )
    )
    action_row = QWidget()
    action_layout = QHBoxLayout(action_row)
    action_layout.setContentsMargins(0, 0, 0, 0)
    back_button = secondary_button("Kembali ke Profil")
    recheck_button = secondary_button("Cek Ulang Sesi")
    open_button = primary_button("Buka / Fokuskan Sesi Login")
    back_button.clicked.connect(lambda checked=False: on_back())
    recheck_button.clicked.connect(lambda checked=False: on_recheck())
    open_button.clicked.connect(lambda checked=False: on_open_login())
    action_layout.addWidget(back_button)
    action_layout.addStretch(1)
    if on_check_flow is not None:
        flow_button = secondary_button("Cek Akses Flow")
        flow_button.setEnabled(profile.state is GoogleSessionState.READY and not flow_busy)
        flow_button.clicked.connect(lambda checked=False: on_check_flow())
        action_layout.addWidget(flow_button)
    action_layout.addWidget(recheck_button)
    action_layout.addWidget(open_button)
    steps_layout.addWidget(action_row)
    layout.addWidget(steps)
    layout.addStretch(1)
    return root
