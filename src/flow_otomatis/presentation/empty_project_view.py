"""Truthful project-free Workspace and Hasil routes in the production shell.

The 30 owner-approved static screenshot fixtures stay untouched.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from flow_otomatis.presentation.widgets import (
    card,
    info_banner,
    muted_label,
    page_header,
    primary_button,
    secondary_button,
)

EmptyProjectRoute = Literal["Workspace", "Hasil"]


def build_empty_project_view(
    route: EmptyProjectRoute,
    *,
    on_home: Callable[[], object],
    on_import: Callable[[], object] | None,
) -> QWidget:
    """Build actionable empty states without inventing projects or MP4 files."""

    if route not in {"Workspace", "Hasil"}:
        raise ValueError("Unsupported project-free route")

    title = (
        "Belum ada Workspace aktif"
        if route == "Workspace"
        else "Belum ada hasil proyek"
    )
    explanation = (
        "Impor paket episode atau buka proyek lokal dari Beranda untuk "
        "menyusun dan memeriksa Scene."
        if route == "Workspace"
        else "Hasil Generate dan Download hanya ditampilkan setelah ada "
        "proyek lokal yang dipilih. Belum ada video untuk diunduh."
    )

    root = QWidget()
    root.setObjectName(f"RealEmpty{route}")
    layout = QVBoxLayout(root)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(18)

    layout.addWidget(page_header(route, "Flow-Otomatis • Mode Lokal"))
    layout.addWidget(
        info_banner(
            "TIDAK ADA PROJECT AKTIF",
            "Data contoh, kredit provider, dan MP4 simulasi tidak digunakan "
            "sebagai status aplikasi nyata.",
            "info",
        )
    )

    panel, body = card(12)
    panel.setObjectName("RealEmptyProjectCard")
    body.addWidget(page_header(title, "Aplikasi menunggu input proyek lokal."))
    body.addWidget(muted_label(explanation))

    import_button = primary_button("Impor Paket Episode")
    import_button.setObjectName("RealEmptyImport")
    if on_import is None:
        import_button.setEnabled(False)
        import_button.setToolTip("Layanan impor paket belum tersedia.")
    else:
        import_button.clicked.connect(on_import)
    body.addWidget(import_button, alignment=Qt.AlignmentFlag.AlignLeft)

    home_button = secondary_button("Buka Beranda")
    home_button.setObjectName("RealEmptyHome")
    home_button.clicked.connect(on_home)
    body.addWidget(home_button, alignment=Qt.AlignmentFlag.AlignLeft)

    layout.addWidget(panel)
    layout.addStretch(1)
    return root
