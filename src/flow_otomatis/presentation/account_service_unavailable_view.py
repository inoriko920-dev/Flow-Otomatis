"""Production-only fail-closed view for unavailable account/key services.

Never render mock Google sessions or mock Gemini API keys in the real app.
The approved frozen STEP 09 screenshot fixtures are unchanged.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from PySide6.QtWidgets import QVBoxLayout, QWidget

from flow_otomatis.presentation.widgets import (
    card,
    info_banner,
    muted_label,
    page_header,
    secondary_button,
)

UnavailableServiceRoute = Literal["Profil Google", "Gemini Keys"]


def build_account_service_unavailable_view(
    route: UnavailableServiceRoute,
    *,
    on_home: Callable[[], object],
    on_diagnostics: Callable[[], object],
    read_error: bool = False,
) -> QWidget:
    """Offer local recovery navigation without claiming any provider access."""

    if route not in {"Profil Google", "Gemini Keys"}:
        raise ValueError("Unsupported provider service route")

    root = QWidget()
    root.setObjectName(
        "RealGoogleProfilesUnavailable" if route == "Profil Google" else "RealGeminiKeysUnavailable"
    )
    layout = QVBoxLayout(root)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(16)
    layout.addWidget(
        page_header(
            route,
            "Mode lokal • Data belum dapat diperiksa"
            if read_error
            else "Mode lokal • Layanan belum dikonfigurasi",
        )
    )

    service_name = "Pengelola sesi Google" if route == "Profil Google" else "Pengelola kunci Gemini"
    detail = (
        f"Status {service_name} gagal dibaca dari penyimpanan lokal. "
        "Data tersimpan tidak diubah. Detail file dan akun disembunyikan."
        if read_error
        else f"{service_name} belum tersedia dalam proses aplikasi ini. "
        "Tidak dapat menampilkan profil atau kunci asli."
    )
    layout.addWidget(
        info_banner(
            "STATUS LAYANAN TIDAK DIKETAHUI" if read_error else "LAYANAN TIDAK TERSEDIA",
            detail
            + " Tidak ada status login, akses Flow, saldo, atau kuota yang "
            "boleh disimpulkan dari layar ini.",
            "warning",
        )
    )
    panel, body = card(10)
    panel.setObjectName("RealUnavailableServiceCard")
    body.addWidget(
        muted_label(
            "Layar contoh tidak digunakan sebagai akun asli. "
            "Aplikasi tidak mencoba login, mengakses API, "
            "menyimpan kredensial, ataupun menjalankan Generate."
        )
    )
    diagnostic = secondary_button("Buka Diagnostik Lokal")
    diagnostic.setObjectName("RealUnavailableServiceDiagnostics")
    diagnostic.clicked.connect(on_diagnostics)
    body.addWidget(diagnostic)
    home = secondary_button("Kembali ke Beranda")
    home.setObjectName("RealUnavailableServiceHome")
    home.clicked.connect(on_home)
    body.addWidget(home)
    layout.addWidget(panel)
    layout.addStretch(1)
    return root
