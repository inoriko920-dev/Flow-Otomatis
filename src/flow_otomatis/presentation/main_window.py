"""Production application shell for the frozen STEP 09 UI."""

from __future__ import annotations

from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.presentation.fixtures import (
    DEFAULT_FIXTURE_CODE,
    NAV_ITEMS,
    get_fixture,
)
from flow_otomatis.presentation.screen_factory import build_right_panel, build_screen
from flow_otomatis.presentation.theme import (
    RIGHT_DOCK_WIDTH,
    SIDEBAR_WIDTH,
    STATUSBAR_HEIGHT,
    TOPBAR_HEIGHT,
    application_stylesheet,
)
from flow_otomatis.presentation.widgets import muted_label, status_badge

_NAV_DEFAULTS = {
    "Beranda": "UI-IMG-001A",
    "Workspace": "UI-IMG-002A",
    "Hasil": "UI-IMG-003A",
    "Profil Google": "UI-IMG-004A",
    "Gemini Keys": "UI-IMG-006A",
    "Diagnostik": "UI-IMG-008A",
    "Pengaturan": "UI-IMG-007A",
}

_NAV_GLYPHS = {
    "Beranda": "⌂",
    "Workspace": "▦",
    "Hasil": "✓",
    "Profil Google": "◉",
    "Gemini Keys": "◆",
    "Diagnostik": "≡",
    "Pengaturan": "⚙",
}


class MainWindow(QMainWindow):
    """Frozen Windows desktop shell used by production and visual fixtures."""

    def __init__(self, fixture_code: str = DEFAULT_FIXTURE_CODE) -> None:
        super().__init__()
        self.setWindowTitle("Flow-Otomatis")
        self.setObjectName("FlowOtomatisMainWindow")
        self.setStyleSheet(application_stylesheet())
        self.resize(1600, 900)
        self.setMinimumSize(1180, 700)

        self._fixture_code = fixture_code
        self._nav_buttons: dict[str, QPushButton] = {}

        root = QWidget()
        root.setObjectName("AppRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_sidebar())

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        body_layout.addWidget(self._build_topbar())

        self._content_row = QWidget()
        content_row_layout = QHBoxLayout(self._content_row)
        content_row_layout.setContentsMargins(0, 0, 0, 0)
        content_row_layout.setSpacing(0)

        self._content_host = QWidget()
        self._content_layout = QVBoxLayout(self._content_host)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        content_row_layout.addWidget(self._content_host, 1)

        self._right_host = QWidget()
        self._right_host.setObjectName("RightDock")
        self._right_host.setFixedWidth(RIGHT_DOCK_WIDTH)
        self._right_layout = QVBoxLayout(self._right_host)
        self._right_layout.setContentsMargins(0, 0, 0, 0)
        self._right_layout.setSpacing(0)
        content_row_layout.addWidget(self._right_host)
        body_layout.addWidget(self._content_row, 1)

        body_layout.addWidget(self._build_statusbar())

        root_layout.addWidget(body, 1)
        self.setCentralWidget(root)
        self.show_fixture(fixture_code)

    @property
    def fixture_code(self) -> str:
        """Return the currently rendered frozen fixture code."""

        return self._fixture_code

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(SIDEBAR_WIDTH)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 16, 14, 14)
        layout.setSpacing(6)

        brand = QLabel("Flow-Otomatis")
        font = QFont(brand.font())
        font.setPointSize(15)
        font.setWeight(QFont.Weight.DemiBold)
        brand.setFont(font)
        layout.addWidget(brand)

        tagline = muted_label("Google Flow Production Manager")
        layout.addWidget(tagline)
        layout.addSpacing(16)

        for item in NAV_ITEMS:
            button = QPushButton(f"{_NAV_GLYPHS[item]}    {item}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.clicked.connect(partial(self._open_navigation_item, item))
            self._nav_buttons[item] = button
            layout.addWidget(button)

        layout.addStretch(1)
        layout.addWidget(status_badge("●  Online", "success"), alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(muted_label("Flow-Otomatis v0.1.0"))
        return sidebar

    def _build_topbar(self) -> QWidget:
        topbar = QWidget()
        topbar.setObjectName("TopBar")
        topbar.setFixedHeight(TOPBAR_HEIGHT)
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(10)

        self._project_label = QLabel("Tidak ada project dipilih")
        project_font = QFont(self._project_label.font())
        project_font.setWeight(QFont.Weight.DemiBold)
        self._project_label.setFont(project_font)
        layout.addWidget(self._project_label)

        self._project_state_label = muted_label("Beranda")
        layout.addWidget(self._project_state_label)
        layout.addStretch(1)

        self._saved_badge = status_badge("Tersimpan", "success")
        layout.addWidget(self._saved_badge)
        layout.addWidget(status_badge("Online", "success"))
        layout.addWidget(QLabel("?"))
        return topbar

    def _build_statusbar(self) -> QWidget:
        statusbar = QWidget()
        statusbar.setObjectName("StatusBar")
        statusbar.setFixedHeight(STATUSBAR_HEIGHT)
        layout = QHBoxLayout(statusbar)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(14)
        layout.addWidget(muted_label("Flow-Otomatis v0.1.0"))
        layout.addWidget(muted_label("Siap digunakan"))
        layout.addStretch(1)
        self._status_project = muted_label("0 project")
        layout.addWidget(self._status_project)
        layout.addWidget(muted_label("Autosave aktif"))
        return statusbar

    def _open_navigation_item(self, item: str, checked: bool = False) -> None:
        del checked
        self.show_fixture(_NAV_DEFAULTS[item])

    def _replace_layout_widget(self, layout: QVBoxLayout, widget: QWidget | None) -> None:
        while layout.count():
            item = layout.takeAt(0)
            old_widget = item.widget()
            if old_widget is not None:
                old_widget.setParent(None)
                old_widget.deleteLater()
        if widget is not None:
            layout.addWidget(widget)

    def show_fixture(self, code: str) -> None:
        """Render one approved visual state inside the production shell."""

        fixture = get_fixture(code)
        self._fixture_code = fixture.code

        for name, button in self._nav_buttons.items():
            button.setChecked(name == fixture.nav_item)

        self._project_state_label.setText(fixture.surface)
        if fixture.code.startswith("UI-IMG-001"):
            self._project_label.setText("Tidak ada project dipilih")
            self._status_project.setText("0 project")
        else:
            self._project_label.setText("EP001 • Steve Jobs")
            self._status_project.setText("EP001 • 60 scene")

        self._replace_layout_widget(self._content_layout, build_screen(fixture))
        right_panel = build_right_panel(fixture)
        self._replace_layout_widget(self._right_layout, right_panel)
        self._right_host.setVisible(right_panel is not None)
