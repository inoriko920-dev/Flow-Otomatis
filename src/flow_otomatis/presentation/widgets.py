"""Shared presentation components for the frozen STEP 09 shell."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.presentation import theme


def page_header(title: str, subtitle: str) -> QWidget:
    """Create a compact title/subtitle block."""

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(3)
    title_label = QLabel(title)
    title_label.setObjectName("PageTitle")
    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("Muted")
    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)
    return widget


def section_header(title: str, detail: str | None = None) -> QWidget:
    """Create a section heading with optional right-aligned detail."""

    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    title_label = QLabel(title)
    title_label.setObjectName("SectionTitle")
    layout.addWidget(title_label)
    layout.addStretch(1)
    if detail:
        detail_label = QLabel(detail)
        detail_label.setObjectName("Muted")
        layout.addWidget(detail_label)
    return widget


def card(spacing: int = 10) -> tuple[QFrame, QVBoxLayout]:
    """Create the canonical bordered white card."""

    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 13, 14, 13)
    layout.setSpacing(spacing)
    return frame, layout


def primary_button(text: str) -> QPushButton:
    """Create a primary blue action."""

    button = QPushButton(text)
    button.setObjectName("Primary")
    return button


def secondary_button(text: str) -> QPushButton:
    """Create a normal secondary action."""

    return QPushButton(text)


def danger_button(text: str) -> QPushButton:
    """Create a red destructive action."""

    button = QPushButton(text)
    button.setObjectName("Danger")
    return button


def muted_label(text: str) -> QLabel:
    """Create secondary supporting copy."""

    label = QLabel(text)
    label.setObjectName("Muted")
    label.setWordWrap(True)
    return label


def status_badge(text: str, kind: str = "neutral") -> QLabel:
    """Create an icon-and-text semantic badge."""

    palette = {
        "success": (theme.SUCCESS_BG, theme.SUCCESS),
        "warning": (theme.WARNING_BG, theme.WARNING),
        "error": (theme.ERROR_BG, theme.ERROR),
        "info": (theme.INFO_BG, theme.PRIMARY),
        "neutral": ("#F3F4F6", "#4B5563"),
    }
    background, foreground = palette.get(kind, palette["neutral"])
    icon = {
        "success": "●",
        "warning": "▲",
        "error": "●",
        "info": "●",
        "neutral": "●",
    }.get(kind, "●")
    label = QLabel(f"{icon}  {text}")
    label.setStyleSheet(
        "QLabel {"
        f"background: {background}; color: {foreground};"
        "border-radius: 9px; padding: 3px 8px; font-weight: 600;"
        "}"
    )
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


def metric_card(title: str, value: str, detail: str, kind: str = "neutral") -> QFrame:
    """Create a compact summary metric card."""

    frame, layout = card(5)
    title_label = muted_label(title)
    value_label = QLabel(value)
    font = QFont(value_label.font())
    font.setPointSize(18)
    font.setWeight(QFont.Weight.DemiBold)
    value_label.setFont(font)
    layout.addWidget(title_label)
    layout.addWidget(value_label)
    layout.addWidget(status_badge(detail, kind), alignment=Qt.AlignmentFlag.AlignLeft)
    return frame


def labeled_value(label: str, value: str, *, strong: bool = False) -> QWidget:
    """Create one compact label/value row."""

    widget = QWidget()
    row = QHBoxLayout(widget)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(8)
    key = QLabel(label)
    key.setObjectName("Muted")
    key.setMinimumWidth(118)
    val = QLabel(value)
    if strong:
        font = QFont(val.font())
        font.setWeight(QFont.Weight.DemiBold)
        val.setFont(font)
    val.setWordWrap(True)
    row.addWidget(key)
    row.addWidget(val, 1)
    return widget


def info_banner(title: str, detail: str, kind: str = "info") -> QFrame:
    """Create a state banner with semantic color."""

    colors = {
        "info": (theme.INFO_BG, theme.PRIMARY),
        "success": (theme.SUCCESS_BG, theme.SUCCESS),
        "warning": (theme.WARNING_BG, theme.WARNING),
        "error": (theme.ERROR_BG, theme.ERROR),
    }
    background, foreground = colors.get(kind, colors["info"])
    frame = QFrame()
    frame.setStyleSheet(
        f"QFrame {{background: {background}; border: 1px solid {foreground};border-radius: 7px;}}"
    )
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 9, 12, 9)
    layout.setSpacing(2)
    title_label = QLabel(title)
    title_font = QFont(title_label.font())
    title_font.setWeight(QFont.Weight.DemiBold)
    title_label.setFont(title_font)
    title_label.setStyleSheet(f"color: {foreground};")
    detail_label = QLabel(detail)
    detail_label.setWordWrap(True)
    detail_label.setStyleSheet(f"color: {foreground};")
    layout.addWidget(title_label)
    layout.addWidget(detail_label)
    return frame


def table_widget(
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    stretch_column: int | None = None,
) -> QTableWidget:
    """Create the canonical read-only data table."""

    table = QTableWidget(len(rows), len(headers))
    table.setHorizontalHeaderLabels(list(headers))
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.setShowGrid(False)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            item = QTableWidgetItem(value)
            item.setTextAlignment(int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft))
            table.setItem(row_index, column_index, item)

    header = table.horizontalHeader()
    for column in range(len(headers)):
        header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
    if stretch_column is not None and 0 <= stretch_column < len(headers):
        header.setSectionResizeMode(stretch_column, QHeaderView.ResizeMode.Stretch)
    table.resizeRowsToContents()
    return table


def progress(value: int, text_visible: bool = False) -> QProgressBar:
    """Create a frozen blue progress indicator."""

    bar = QProgressBar()
    bar.setRange(0, 100)
    bar.setValue(max(0, min(value, 100)))
    bar.setTextVisible(text_visible)
    return bar
