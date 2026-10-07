"""Frozen light-theme tokens for STEP 09."""

from __future__ import annotations

PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
BACKGROUND = "#F5F7FA"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F8FAFC"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#D8DEE8"
SUCCESS = "#15803D"
SUCCESS_BG = "#DCFCE7"
WARNING = "#B45309"
WARNING_BG = "#FEF3C7"
ERROR = "#B91C1C"
ERROR_BG = "#FEE2E2"
INFO_BG = "#DBEAFE"
SIDEBAR_WIDTH = 216
TOPBAR_HEIGHT = 56
RIGHT_DOCK_WIDTH = 376
STATUSBAR_HEIGHT = 28


def application_stylesheet() -> str:
    """Return the single canonical QSS for the frozen light shell."""

    return f"""
    * {{
        font-family: "Segoe UI Variable", "Segoe UI";
        font-size: 9pt;
        color: {TEXT};
    }}
    QMainWindow, QWidget#AppRoot {{
        background: {BACKGROUND};
    }}
    QWidget#Sidebar, QWidget#TopBar, QWidget#StatusBar, QFrame#Card, QFrame#RightDock {{
        background: {SURFACE};
    }}
    QWidget#Sidebar {{
        border-right: 1px solid {BORDER};
    }}
    QWidget#TopBar {{
        border-bottom: 1px solid {BORDER};
    }}
    QWidget#StatusBar {{
        border-top: 1px solid {BORDER};
    }}
    QFrame#Card {{
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    QLabel#Muted {{
        color: {MUTED};
    }}
    QLabel#SectionTitle {{
        font-size: 11pt;
        font-weight: 600;
    }}
    QLabel#PageTitle {{
        font-size: 16pt;
        font-weight: 650;
    }}
    QPushButton {{
        min-height: 32px;
        padding: 0 12px;
        border: 1px solid {BORDER};
        border-radius: 6px;
        background: {SURFACE};
    }}
    QPushButton:hover {{
        background: {SURFACE_ALT};
    }}
    QPushButton#Primary {{
        background: {PRIMARY};
        color: white;
        border-color: {PRIMARY};
        font-weight: 600;
    }}
    QPushButton#Primary:hover {{
        background: {PRIMARY_HOVER};
    }}
    QPushButton#Danger {{
        background: #DC2626;
        color: white;
        border-color: #DC2626;
        font-weight: 600;
    }}
    QPushButton#NavButton {{
        min-height: 38px;
        border: 0;
        border-radius: 6px;
        text-align: left;
        padding-left: 14px;
        background: transparent;
        color: #374151;
    }}
    QPushButton#NavButton:checked {{
        background: {INFO_BG};
        color: {PRIMARY};
        font-weight: 600;
    }}
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 8px;
        selection-background-color: {INFO_BG};
    }}
    QTableWidget {{
        background: {SURFACE};
        alternate-background-color: {SURFACE_ALT};
        border: 1px solid {BORDER};
        border-radius: 7px;
        gridline-color: #E5E7EB;
    }}
    QHeaderView::section {{
        background: {SURFACE_ALT};
        border: 0;
        border-bottom: 1px solid {BORDER};
        padding: 7px 6px;
        color: #4B5563;
        font-weight: 600;
    }}
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        background: {SURFACE};
    }}
    QTabBar::tab {{
        background: {SURFACE_ALT};
        padding: 7px 12px;
        border: 1px solid {BORDER};
        border-bottom: 0;
    }}
    QTabBar::tab:selected {{
        background: {SURFACE};
        color: {PRIMARY};
        font-weight: 600;
    }}
    QProgressBar {{
        min-height: 14px;
        max-height: 14px;
        border: 1px solid {BORDER};
        border-radius: 7px;
        background: {SURFACE_ALT};
        text-align: center;
    }}
    QProgressBar::chunk {{
        background: {PRIMARY};
        border-radius: 6px;
    }}
    """
