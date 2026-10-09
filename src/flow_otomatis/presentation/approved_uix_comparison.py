"""Read-only side-by-side viewer for an approved PNG and the running Qt UI."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.presentation import theme


class ApprovedUixComparisonDialog(QDialog):
    """Never rewrites the frozen reference or invokes provider/UI automation."""

    def __init__(
        self,
        state_code: str,
        approved_image: Path,
        current_view: QPixmap,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ApprovedUixComparisonDialog")
        self.setWindowTitle(f"{state_code} | Bandingkan UI Final dan Qt")
        self.setMinimumSize(980, 630)
        self.resize(1700, 790)
        self.setStyleSheet(theme.application_stylesheet())
        if current_view.isNull():
            raise ValueError("Gambar layar Qt tidak tersedia.")
        owner_image = QPixmap(str(approved_image))
        if owner_image.isNull():
            raise ValueError("Gambar referensi final tidak dapat dibuka.")

        layout = QVBoxLayout(self)
        intro = QLabel(
            f"{state_code} • PNG FINAL disetujui (SHA-256 cocok) dibandingkan "
            "dengan render Qt saat ini. Ini pratinjau, bukan uji pixel-parity."
        )
        intro.setObjectName("UixComparisonInfo")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        body = QWidget()
        cols = QHBoxLayout(body)
        cols.setContentsMargins(8, 8, 8, 8)
        cols.setSpacing(16)
        for title, pixmap in (
            ("KIRI • Desain referensi asli 1920×1080", owner_image),
            ("KANAN • Aplikasi Qt yang sedang berjalan", current_view),
        ):
            column = QWidget()
            vertical = QVBoxLayout(column)
            heading = QLabel(title)
            heading.setObjectName("UixComparisonLabel")
            heading.setStyleSheet(
                f"font-size: 11pt; font-weight: 600; color: {theme.PRIMARY};"
            )
            vertical.addWidget(heading)
            visual = QLabel()
            visual.setObjectName("UixComparisonImage")
            visual.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            visual.setPixmap(
                pixmap.scaled(
                    820,
                    462,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            visual.setMinimumSize(820, 462)
            vertical.addWidget(visual)
            vertical.addWidget(
                QLabel(f"Sumber: {pixmap.width()} × {pixmap.height()} piksel")
            )
            vertical.addStretch(1)
            cols.addWidget(column)

        scroller = QScrollArea()
        scroller.setObjectName("UixComparisonScroll")
        scroller.setWidgetResizable(True)
        scroller.setWidget(body)
        layout.addWidget(scroller, 1)

        note = QLabel(
            "Pemeriksaan manual wajib: tata letak, teks, ukuran kontrol, warna, "
            "dan pesan. Tidak ada perubahan pada PNG acuan atau akun Google."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        close = QPushButton("Tutup Perbandingan")
        close.setObjectName("UixComparisonClose")
        close.clicked.connect(self.accept)
        layout.addWidget(close, alignment=Qt.AlignmentFlag.AlignRight)
