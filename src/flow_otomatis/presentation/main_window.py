"""Production application shell for the frozen STEP 09 UI."""

from __future__ import annotations

import json
from concurrent.futures import Future
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide6.QtGui import QCloseEvent, QFont, QKeyEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from flow_otomatis.application.ports import (
    GoogleFlowAccessProbe,
    GoogleSessionProfile,
    GoogleSessionState,
)
from flow_otomatis.application.ports.episode_package import EpisodeImageVerifierPort
from flow_otomatis.application.services import (
    EpisodeImportService,
    GeminiAgentReply,
    GeminiAgentService,
    GeminiKeyService,
    GoogleFlowPreflightService,
    GoogleSessionService,
    LocalResultsService,
    ProjectLibraryService,
    ScenePlanningService,
)
from flow_otomatis.domain.errors import (
    FlowOtomatisError,
    InternalInvariantError,
    StorageError,
    WorkspaceAlreadyExistsError,
    WorkspaceCorruptError,
)
from flow_otomatis.domain.gemini import GeminiKeyProfile
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.presentation.credit_uix_preview import CreditUixDialog
from flow_otomatis.presentation.diagnostics_view import (
    LocalDiagnosticSnapshot,
    build_local_diagnostics_view,
)
from flow_otomatis.presentation.empty_project_view import build_empty_project_view
from flow_otomatis.presentation.fixtures import (
    DEFAULT_FIXTURE_CODE,
    NAV_ITEMS,
    get_fixture,
)
from flow_otomatis.presentation.gemini_keys_view import build_gemini_keys_view
from flow_otomatis.presentation.google_profiles_view import (
    build_google_login_view,
    build_google_profiles_view,
)
from flow_otomatis.presentation.local_scene_preflight_view import LocalScenePreflightDialog
from flow_otomatis.presentation.project_hub_view import (
    build_project_hub_unavailable_view,
    build_project_hub_view,
)
from flow_otomatis.presentation.results_view import build_results_view
from flow_otomatis.presentation.screen_factory import build_right_panel, build_screen
from flow_otomatis.presentation.settings_view import (
    LocalSettingsSnapshot,
    build_local_settings_view,
)
from flow_otomatis.presentation.theme import (
    RIGHT_DOCK_WIDTH,
    SIDEBAR_WIDTH,
    STATUSBAR_HEIGHT,
    TOPBAR_HEIGHT,
    application_stylesheet,
)
from flow_otomatis.presentation.widgets import muted_label, status_badge
from flow_otomatis.presentation.workspace_views import (
    build_validation_view,
    build_workspace_right_panel,
    build_workspace_view,
)

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


@dataclass(frozen=True, slots=True)
class _GeminiAgentRequest:
    """An immutable completion right bound to one displayed project/Scene."""

    request_id: int
    episode_id: str
    scene_id: str
    context_generation: int


class _GeminiAgentSignals(QObject):
    """One independent Qt signal bridge per Agent request (not window-owned)."""

    answered = Signal(object, object)
    failed = Signal(object, str)


class _GeminiAgentTask(QRunnable):
    """Run one Gemini Agent request away from the Qt event loop."""

    def __init__(
        self,
        service: GeminiAgentService,
        workspace: WorkspaceState,
        scene_id: str,
        question: str,
        request: _GeminiAgentRequest,
        signals: _GeminiAgentSignals,
    ) -> None:
        super().__init__()
        self._service = service
        self._workspace = workspace
        self._scene_id = scene_id
        self._question = question
        self._request = request
        self._signals = signals

    @Slot()
    def run(self) -> None:
        try:
            reply = self._service.ask(self._workspace, self._scene_id, self._question)
        except FlowOtomatisError as exc:
            self._signals.failed.emit(self._request, str(exc))
        except Exception:
            self._signals.failed.emit(
                self._request,
                "AI Agent gagal tanpa mengekspos secret atau detail provider.",
            )
        else:
            self._signals.answered.emit(self._request, reply)


class _GeminiHealthSignals(QObject):
    """Return sanitized Gemini health metadata to the Qt thread."""

    checked = Signal(object)
    failed = Signal(str)


class _GeminiHealthTask(QRunnable):
    """Run one network health check without blocking Qt."""

    def __init__(
        self,
        service: GeminiKeyService,
        key_id: str,
        signals: _GeminiHealthSignals,
    ) -> None:
        super().__init__()
        self._service = service
        self._key_id = key_id
        self._signals = signals

    @Slot()
    def run(self) -> None:
        try:
            profile = self._service.check_health(self._key_id)
        except FlowOtomatisError as exc:
            self._signals.failed.emit(str(exc))
        except Exception:
            self._signals.failed.emit("Cek Gemini key gagal tanpa mengekspos secret.")
        else:
            self._signals.checked.emit(profile)


class _GoogleSessionSignals(QObject):
    """Marshal sanitized Browser Worker outcomes back onto the Qt thread."""

    profile_ready = Signal(str, object)
    all_ready = Signal()
    failed = Signal(str, str)


class _GoogleFlowSignals(QObject):
    """Emit sanitized read-only Flow results to the Qt owner thread."""

    checked = Signal(str, int, object)
    failed = Signal(str, int, str)


_DIALOG_BACKGROUNDS = {
    "UI-IMG-001C": "UI-IMG-001A",
    "UI-IMG-012A": "UI-IMG-002A",
    "UI-IMG-012B": "UI-IMG-002A",
    "UI-IMG-013A": "UI-IMG-004B",
    "UI-IMG-014A": "UI-IMG-002B",
    "UI-IMG-015A": "UI-IMG-007A",
}


class MainWindow(QMainWindow):
    """Frozen shell plus real-state wiring introduced by STEP 10/11."""

    def __init__(
        self,
        fixture_code: str = DEFAULT_FIXTURE_CODE,
        *,
        episode_import_service: EpisodeImportService | None = None,
        scene_planning_service: ScenePlanningService | None = None,
        image_verifier: EpisodeImageVerifierPort | None = None,
        project_library_service: ProjectLibraryService | None = None,
        local_results_service: LocalResultsService | None = None,
        google_session_service: GoogleSessionService | None = None,
        google_flow_preflight_service: GoogleFlowPreflightService | None = None,
        gemini_key_service: GeminiKeyService | None = None,
        gemini_agent_service: GeminiAgentService | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Flow-Otomatis")
        self.setObjectName("FlowOtomatisMainWindow")
        self.setStyleSheet(application_stylesheet())
        self.resize(1600, 900)
        self.setMinimumSize(1180, 700)

        self._fixture_code = fixture_code
        self._production_shell = False
        self._nav_buttons: dict[str, QPushButton] = {}
        self._episode_import_service = episode_import_service
        self._scene_planning_service = scene_planning_service
        self._image_verifier = image_verifier
        self._project_library_service = project_library_service
        self._local_results_service = local_results_service
        self._google_session_service = google_session_service
        self._google_flow_preflight_service = google_flow_preflight_service
        self._google_flow_probes: dict[str, GoogleFlowAccessProbe] = {}
        self._google_flow_epochs: dict[str, int] = {}
        self._google_flow_busy: set[str] = set()
        self._google_browser_closed = False
        self._gemini_key_service = gemini_key_service
        self._gemini_agent_service = gemini_agent_service
        self._agent_answer: str | None = None
        self._agent_busy = False
        self._agent_request_id = 0
        self._agent_context_generation = 0
        self._active_agent_request: _GeminiAgentRequest | None = None
        self._agent_closed = False
        self._active_google_profile_id: str | None = None
        self._last_result_manifest_path: Path | None = None
        self._pending_workspace: WorkspaceState | None = None
        self._current_workspace: WorkspaceState | None = None
        self._selected_scene_id: str | None = None
        self._active_uix_preview: CreditUixDialog | None = None
        self._uix_return_workspace: WorkspaceState | None = None
        self._last_diagnostics_snapshot: LocalDiagnosticSnapshot | None = None
        self._google_session_signals = _GoogleSessionSignals(self)
        self._google_session_signals.profile_ready.connect(self._on_google_session_profile_ready)
        self._google_session_signals.all_ready.connect(self.show_google_profiles)
        self._google_session_signals.failed.connect(self._show_google_session_error)
        self._google_flow_signals = _GoogleFlowSignals(self)
        self._google_flow_signals.checked.connect(self._on_google_flow_checked)
        self._google_flow_signals.failed.connect(self._on_google_flow_failed)
        self._gemini_health_signals = _GeminiHealthSignals(self)
        self._gemini_health_signals.checked.connect(self._on_gemini_health_checked)
        self._gemini_health_signals.failed.connect(self._show_gemini_health_error)

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
        """Return the currently rendered frozen/dynamic route code."""

        return self._fixture_code

    @property
    def current_workspace(self) -> WorkspaceState | None:
        """Return the real persisted workspace currently shown, if any."""

        return self._current_workspace

    @property
    def last_result_manifest_path(self) -> Path | None:
        """Return the most recent local handoff manifest exported by this window."""

        return self._last_result_manifest_path

    def configure_production_shell(self) -> None:
        """Never present frozen mock Online/Autosave badges in a real app run.

        Explicit --fixture visual-capture sessions remain pixel-identical.
        This is UI presentation only, not a Google Flow network probe.
        """

        self._production_shell = True
        current_route = next(
            (name for name, button in self._nav_buttons.items() if button.isChecked()),
            "Beranda",
        )
        self._set_navigation(current_route)

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
        self._sidebar_connection_badge = status_badge("●  Online", "success")
        self._sidebar_connection_original_style = self._sidebar_connection_badge.styleSheet()
        layout.addWidget(self._sidebar_connection_badge, alignment=Qt.AlignmentFlag.AlignLeft)
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
        self._saved_badge_original_style = self._saved_badge.styleSheet()
        self._local_badge_style = status_badge("Mode Lokal", "neutral").styleSheet()
        layout.addWidget(self._saved_badge)
        self._connection_badge = status_badge("Online", "success")
        self._connection_badge_original_style = self._connection_badge.styleSheet()
        layout.addWidget(self._connection_badge)
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
        self._runtime_status = muted_label("Siap digunakan")
        layout.addWidget(self._runtime_status)
        layout.addStretch(1)
        self._status_project = muted_label("0 project")
        layout.addWidget(self._status_project)
        self._autosave_label = muted_label("Autosave aktif")
        layout.addWidget(self._autosave_label)
        return statusbar

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Close frozen/dynamic modal states with Escape."""

        if event.key() == Qt.Key.Key_Escape:
            if self._fixture_code in _DIALOG_BACKGROUNDS:
                self.show_fixture(_DIALOG_BACKGROUNDS[self._fixture_code])
                event.accept()
                return
            if self._fixture_code == "REAL_VALIDATION":
                self.show_project_hub()
                event.accept()
                return
            if self._fixture_code == "REAL_UIX22_PREVIEW" and self._active_uix_preview is not None:
                # Keyboard-only exit must follow the same safe workspace
                # return path as the visible Back button.
                self._active_uix_preview.reject()
                event.accept()
                return
        super().keyPressEvent(event)

    def _open_navigation_item(self, item: str, checked: bool = False) -> None:
        del checked
        if item == "Beranda" and self._project_library_service is not None:
            self.show_project_hub()
            return
        if item == "Workspace" and self._current_workspace is not None:
            self.show_workspace_state(self._current_workspace)
            return
        if (
            self._production_shell
            and item in {"Workspace", "Hasil"}
            and self._current_workspace is None
        ):
            self.show_empty_project_route(item)
            return
        if (
            item == "Hasil"
            and self._current_workspace is not None
            and self._local_results_service is not None
        ):
            previous_navigation = next(
                (
                    name
                    for name, button in self._nav_buttons.items()
                    if name != "Hasil" and button.isChecked()
                ),
                "Hasil",
            )
            try:
                self.show_results_state()
            except FlowOtomatisError:
                # Keep the current view usable when persisted result history fails.
                self._set_navigation(previous_navigation)
                QMessageBox.warning(
                    self,
                    "Hasil Tidak Dapat Dibuka",
                    "Data hasil project tidak dapat dibaca. Periksa penyimpanan atau "
                    "pulihkan data yang rusak dari backup, lalu coba kembali.",
                )
            return
        if item == "Profil Google" and self._google_session_service is not None:
            self.show_google_profiles()
            return
        if item == "Gemini Keys" and self._gemini_key_service is not None:
            self.show_gemini_keys()
            return
        if item == "Diagnostik" and self._production_shell:
            self.show_local_diagnostics()
            return
        if item == "Pengaturan" and self._production_shell:
            self.show_local_settings()
            return
        self.show_fixture(_NAV_DEFAULTS[item])

    def _replace_layout_widget(self, layout: QVBoxLayout, widget: QWidget | None) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                break
            old_widget = item.widget()
            if old_widget is not None:
                if old_widget is self._active_uix_preview:
                    self._active_uix_preview = None
                    self._uix_return_workspace = None
                old_widget.setParent(None)
                old_widget.deleteLater()
        if widget is not None:
            layout.addWidget(widget)

    def _set_navigation(self, item: str) -> None:
        for name, button in self._nav_buttons.items():
            button.setChecked(name == item)
        if self._production_shell or self._fixture_code.startswith("REAL_"):
            # A running desktop app does NOT prove Google Flow workspace access.
            self._connection_badge.setText("●  Mode Lokal")
            self._connection_badge.setStyleSheet(self._local_badge_style)
            self._sidebar_connection_badge.setText("●  Mode Lokal")
            self._sidebar_connection_badge.setToolTip(
                "Flow belum terverifikasi. Ini hanya status data/aplikasi lokal."
            )
            self._sidebar_connection_badge.setStyleSheet(self._local_badge_style)
            self._saved_badge.setText("●  Data Lokal")
            self._saved_badge.setStyleSheet(self._local_badge_style)
            self._runtime_status.setText("Mode lokal • Generate Flow belum aktif")
            self._autosave_label.setText("Penyimpanan lokal")
        else:
            # Exact approved frozen STEP 09 reference appearance.
            self._connection_badge.setText("●  Online")
            self._connection_badge.setStyleSheet(self._connection_badge_original_style)
            self._sidebar_connection_badge.setText("●  ●  Online")
            self._sidebar_connection_badge.setToolTip("")
            self._sidebar_connection_badge.setStyleSheet(self._sidebar_connection_original_style)
            self._saved_badge.setText("●  Tersimpan")
            self._saved_badge.setStyleSheet(self._saved_badge_original_style)
            self._runtime_status.setText("Siap digunakan")
            self._autosave_label.setText("Autosave aktif")

    def _set_project_chrome(self, workspace: WorkspaceState, surface: str) -> None:
        self._project_label.setText(f"{workspace.episode_id} • {workspace.project_name}")
        self._project_state_label.setText(surface)
        self._status_project.setText(f"{workspace.episode_id} • {len(workspace.scenes)} scene")

    def show_fixture(self, code: str) -> None:
        """Render one approved visual state inside the production shell."""

        self._invalidate_agent_context()
        fixture = get_fixture(code)
        self._fixture_code = fixture.code
        self._set_navigation(fixture.nav_item)

        self._project_state_label.setText(fixture.surface)
        if fixture.code.startswith("UI-IMG-001"):
            self._project_label.setText("Tidak ada project dipilih")
            self._status_project.setText("0 project")
        else:
            self._project_label.setText("EP001 • Steve Jobs")
            self._status_project.setText("EP001 • 60 scene")

        if self._production_shell:
            # Some sidebar routes still contain frozen example-only content.
            # Show an unmistakable banner; do not let the owner mistake
            # synthetic profiles, output MP4 or credits for persisted data.
            self._project_label.setText("Pratinjau • Belum ada data proyek")
            self._project_state_label.setText(f"{fixture.surface} • CONTOH")
            self._status_project.setText("DATA CONTOH")
            self._runtime_status.setText("Layar contoh • Generate Flow belum aktif")

        screen = build_screen(fixture)
        self._replace_layout_widget(self._content_layout, screen)
        right_panel = build_right_panel(fixture)
        self._replace_layout_widget(self._right_layout, right_panel)
        self._right_host.setVisible(right_panel is not None)
        self._wire_import_button(screen)

    def show_project_hub(self) -> None:
        """Render real local recent projects using the frozen Project Hub."""

        if self._project_library_service is None:
            if self._production_shell:
                self._show_project_hub_unavailable(missing_service=True)
            else:
                self.show_fixture("UI-IMG-001A")
            return
        self._invalidate_agent_context()
        try:
            scan = self._project_library_service.scan_recent()
        except FlowOtomatisError, OSError, ValueError:
            # A broken/unreadable library does NOT prove there are no projects.
            # Keep raw filesystem paths and exception details off the screen.
            self._show_project_hub_unavailable(missing_service=False)
            return
        workspaces = scan.workspaces
        self._fixture_code = "REAL_PROJECT_HUB"
        self._set_navigation("Beranda")
        self._project_label.setText("Project lokal")
        self._project_state_label.setText("Beranda")
        if scan.issues:
            self._status_project.setText(
                f"{len(workspaces)} project • {len(scan.issues)} bermasalah"
            )
        else:
            self._status_project.setText(f"{len(workspaces)} project")
        view = build_project_hub_view(
            workspaces,
            issues=scan.issues,
            on_open=self._open_local_project_from_ui,
            on_import=self._choose_episode_package,
            on_preview_ui=self.open_credit_uix_preview,
            import_available=self._episode_import_service is not None,
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def _show_project_hub_unavailable(self, *, missing_service: bool) -> None:
        """Expose a safe retry path, not a misleading empty project list."""

        self._invalidate_agent_context()
        self._fixture_code = "REAL_PROJECT_HUB_UNAVAILABLE"
        self._set_navigation("Beranda")
        self._project_label.setText("Project lokal")
        self._project_state_label.setText("Beranda • Belum dapat diperiksa")
        self._status_project.setText("Status project tidak diketahui")
        view = build_project_hub_unavailable_view(
            on_retry=self.show_project_hub,
            on_diagnostics=self.show_local_diagnostics,
            missing_service=missing_service,
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def show_empty_project_route(self, route: str) -> None:
        """No fake Scene, Download history or MP4 when no project is open."""

        if route not in {"Workspace", "Hasil"}:
            raise ValueError("Only project-dependent routes may use an empty state")
        self._invalidate_agent_context()
        self._fixture_code = f"REAL_EMPTY_{route.upper()}"
        self._set_navigation(route)
        self._project_label.setText("Tidak ada project dipilih")
        self._project_state_label.setText(f"{route} • Belum ada project")
        self._status_project.setText("0 project aktif")
        view = build_empty_project_view(
            "Workspace" if route == "Workspace" else "Hasil",
            on_home=self.show_project_hub,
            on_import=(
                self._choose_episode_package if self._episode_import_service is not None else None
            ),
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def show_local_diagnostics(self) -> None:
        """Show facts from local persistence without any provider interaction."""

        if self._project_library_service is None:
            snapshot = LocalDiagnosticSnapshot(
                None,
                None,
                len(self._current_workspace.scenes)
                if self._current_workspace is not None
                else None,
            )
        else:
            try:
                scan = self._project_library_service.scan_recent(limit=10)
            except FlowOtomatisError, OSError, ValueError:
                # Fail closed: no raw exception, project path or account data in UI.
                snapshot = LocalDiagnosticSnapshot(
                    None,
                    None,
                    len(self._current_workspace.scenes)
                    if self._current_workspace is not None
                    else None,
                )
            else:
                snapshot = LocalDiagnosticSnapshot(
                    recent_project_count=len(scan.workspaces),
                    recent_project_issue_count=len(scan.issues),
                    active_scene_count=(
                        len(self._current_workspace.scenes)
                        if self._current_workspace is not None
                        else None
                    ),
                )
        self._invalidate_agent_context()
        self._fixture_code = "REAL_DIAGNOSTICS"
        self._set_navigation("Diagnostik")
        self._project_label.setText("Diagnostik lokal")
        self._project_state_label.setText("Pemeriksaan aplikasi")
        self._status_project.setText("Hanya data lokal")
        self._last_diagnostics_snapshot = snapshot
        view = build_local_diagnostics_view(
            snapshot,
            on_refresh=self.show_local_diagnostics,
            on_export=lambda: self._export_local_diagnostics(snapshot),
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def _export_local_diagnostics(self, snapshot: LocalDiagnosticSnapshot) -> None:
        """Write a sanitized JSON only after explicit operator file selection."""

        if (
            self._fixture_code != "REAL_DIAGNOSTICS"
            or self._last_diagnostics_snapshot is not snapshot
        ):
            return
        filename, _filter = QFileDialog.getSaveFileName(
            self, "Ekspor diagnostik lokal tanpa rahasia", "diagnostik_lokal.json", "JSON (*.json)"
        )
        if not filename:
            return
        try:
            with Path(filename).open("x", encoding="utf-8") as output:
                json.dump(snapshot.as_report(), output, indent=2, ensure_ascii=False)
                output.write("\n")
        except FileExistsError:
            QMessageBox.warning(self, "File sudah ada", "File diagnostik lama tidak akan ditimpa.")
        except OSError:
            QMessageBox.warning(
                self, "Ekspor gagal", "Tidak dapat menyimpan laporan diagnostik lokal."
            )

    def show_local_settings(self) -> None:
        """Display locked settings from the actual local app/Workspace context."""

        workspace = self._current_workspace
        snapshot = LocalSettingsSnapshot(
            active_workspace_model=workspace.model if workspace is not None else None,
            active_workspace_resolution=(workspace.resolution if workspace is not None else None),
            active_workspace_aspect_ratio=(
                workspace.aspect_ratio if workspace is not None else None
            ),
            active_workspace_scene_count=(len(workspace.scenes) if workspace is not None else None),
        )
        self._invalidate_agent_context()
        self._fixture_code = "REAL_SETTINGS"
        self._set_navigation("Pengaturan")
        self._project_label.setText("Konfigurasi lokal")
        self._project_state_label.setText("Pengaturan • Hanya baca")
        self._status_project.setText("Tidak ada akses provider live")
        view = build_local_settings_view(snapshot, on_refresh=self.show_local_settings)
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def _open_local_project_from_ui(self, episode_id: str) -> None:
        """Open a Project Hub row without leaking storage/decode failures to Qt."""

        try:
            self.open_local_project(episode_id)
        except WorkspaceCorruptError:
            QMessageBox.warning(
                self,
                "Project Data Rusak",
                (
                    f"Project {episode_id} tidak dapat dibuka karena data lokalnya rusak. "
                    "File project tidak diubah. Pulihkan dari backup atau salinan yang sehat."
                ),
            )
        except StorageError:
            QMessageBox.warning(
                self,
                "Project Tidak Tersedia",
                (f"Project {episode_id} sementara tidak dapat dibaca. File project tidak diubah."),
            )
        except FlowOtomatisError:
            QMessageBox.warning(
                self,
                "Project Tidak Dapat Dibuka",
                f"Project {episode_id} tidak dapat dibuka dari penyimpanan lokal.",
            )

    def open_local_project(self, episode_id: str) -> WorkspaceState:
        """Open/recover one persisted workspace into the active session."""

        if self._project_library_service is None:
            raise InternalInvariantError("Project library service is not configured")
        workspace = self._project_library_service.open_project(episode_id)
        self._current_workspace = workspace
        self._selected_scene_id = workspace.scenes[0].scene_id if workspace.scenes else None
        self.show_workspace_state(workspace)
        return workspace

    def show_results_state(self) -> None:
        """Render real local Generate/Download facts in the frozen Hasil screen."""

        if self._local_results_service is None:
            raise InternalInvariantError("Local results service is not configured")
        if self._current_workspace is None:
            raise InternalInvariantError("No active workspace")
        results = self._local_results_service.snapshot(self._current_workspace.episode_id)
        self._invalidate_agent_context()
        self._fixture_code = "REAL_RESULTS"
        self._set_navigation("Hasil")
        self._set_project_chrome(self._current_workspace, "Hasil")
        view = build_results_view(
            results,
            on_export_manifest=self._export_result_manifest_from_ui,
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def _export_result_manifest_from_ui(self) -> None:
        """Keep expected storage/export failures inside the Qt command boundary."""

        try:
            self.export_current_result_manifest()
        except FlowOtomatisError, OSError:
            QMessageBox.warning(
                self,
                "Ekspor Hasil Gagal",
                "Hasil belum berhasil diekspor. Periksa data project, ruang kosong, "
                "dan izin folder tujuan, lalu coba kembali.",
            )

    def export_current_result_manifest(self) -> Path:
        """Export the current credential-free FLOW_OTOMATIS_RESULT.json."""

        if self._local_results_service is None:
            raise InternalInvariantError("Local results service is not configured")
        if self._current_workspace is None:
            raise InternalInvariantError("No active workspace")
        self._last_result_manifest_path = None
        path = self._local_results_service.export_manifest(self._current_workspace.episode_id)
        self._last_result_manifest_path = path
        return path

    def show_gemini_keys(self) -> None:
        """Render real credential-free Gemini key metadata."""

        if self._gemini_key_service is None:
            self.show_fixture("UI-IMG-006A")
            return
        self._invalidate_agent_context()
        profiles = self._gemini_key_service.list_profiles()
        self._fixture_code = "REAL_GEMINI_KEYS"
        self._set_navigation("Gemini Keys")
        self._project_label.setText("Gemini API")
        self._project_state_label.setText("Gemini Keys")
        self._status_project.setText(f"{len(profiles)} key")
        view = build_gemini_keys_view(
            profiles,
            on_import=self._import_gemini_keys,
            on_check=self._check_gemini_key,
            on_activate=self._activate_gemini_key,
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def _import_gemini_keys(self) -> None:
        if self._gemini_key_service is None:
            return
        raw, accepted = QInputDialog.getMultiLineText(
            self,
            "Impor Gemini Keys",
            "Paste satu key per baris, atau format Label | Key. Maksimal 100 key.",
        )
        if not accepted or not raw.strip():
            return
        try:
            summary = self._gemini_key_service.import_text(raw)
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Gemini Keys", str(exc))
            return
        QMessageBox.information(
            self,
            "Gemini Keys",
            (
                f"{len(summary.imported)} key disimpan aman. "
                f"{summary.duplicate_count} duplikat dilewati. "
                f"{summary.rejected_count} baris ditolak."
            ),
        )
        self.show_gemini_keys()

    def _check_gemini_key(self, key_id: str) -> None:
        if self._gemini_key_service is None:
            return
        task = _GeminiHealthTask(
            self._gemini_key_service,
            key_id,
            self._gemini_health_signals,
        )
        QThreadPool.globalInstance().start(task)

    def _activate_gemini_key(self, key_id: str) -> None:
        if self._gemini_key_service is None:
            return
        try:
            self._gemini_key_service.set_active(key_id)
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Gemini Keys", str(exc))
            return
        self.show_gemini_keys()

    def _on_gemini_health_checked(self, _profile: GeminiKeyProfile) -> None:
        self.show_gemini_keys()

    def _show_gemini_health_error(self, message: str) -> None:
        QMessageBox.warning(self, "Gemini Keys", message)

    def show_google_profiles(self) -> None:
        """Render real credential-free Google profile/session state."""

        if self._google_session_service is None:
            self.show_fixture("UI-IMG-004A")
            return
        self._invalidate_agent_context()
        profiles = self._google_session_service.list_profiles()
        self._fixture_code = "REAL_GOOGLE_PROFILES"
        self._active_google_profile_id = None
        self._set_navigation("Profil Google")
        self._project_label.setText("Session Google terotorisasi")
        self._project_state_label.setText("Profil Google")
        self._status_project.setText(f"{len(profiles)} profil")
        view = build_google_profiles_view(
            profiles,
            on_add=self._add_google_profile,
            on_check_all=self._check_all_google_profiles,
            on_open_login=self._open_google_login,
            on_check=self._check_google_profile,
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def show_google_login(self, profile: GoogleSessionProfile) -> None:
        """Render real manual-login help for one authorized profile context."""

        self._invalidate_agent_context()
        self._fixture_code = "REAL_GOOGLE_LOGIN"
        self._active_google_profile_id = profile.profile_id
        self._set_navigation("Profil Google")
        self._project_label.setText(profile.label)
        self._project_state_label.setText("Bantuan Login")
        self._status_project.setText("Sesi user-owned")
        if self._google_session_service is None:
            raise InternalInvariantError("Google session service is not configured")
        restart_gate = self._google_session_service.get_restart_gate(profile.profile_id)
        view = build_google_login_view(
            profile,
            restart_gate=restart_gate,
            flow_probe=self._google_flow_probes.get(profile.profile_id),
            flow_busy=profile.profile_id in self._google_flow_busy,
            on_check_flow=(
                self._check_active_google_flow
                if self._google_flow_preflight_service is not None
                else None
            ),
            on_open_login=self._reopen_active_google_login,
            on_recheck=self._recheck_active_google_login,
            on_back=self.show_google_profiles,
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def _add_google_profile(self) -> None:
        if self._google_session_service is None:
            return
        label, accepted = QInputDialog.getText(
            self,
            "Tambah Profil Google",
            "Nama profil lokal:",
        )
        if not accepted:
            return
        try:
            profile = self._google_session_service.create_profile(label)
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Profil Google", str(exc))
            return
        self.show_google_login(profile)

    def _open_google_login(self, profile_id: str) -> None:
        if self._google_session_service is None:
            return
        self._invalidate_google_flow(profile_id)
        future = self._google_session_service.open_login_async(profile_id)
        self._watch_google_profile_future(future, "open", "Bantuan Login")

    def _reopen_active_google_login(self) -> None:
        if self._active_google_profile_id is None:
            self.show_google_profiles()
            return
        self._open_google_login(self._active_google_profile_id)

    def _recheck_active_google_login(self) -> None:
        if self._google_session_service is None or self._active_google_profile_id is None:
            self.show_google_profiles()
            return
        self._invalidate_google_flow(self._active_google_profile_id)
        future = self._google_session_service.check_profile_async(self._active_google_profile_id)
        self._watch_google_profile_future(future, "recheck", "Bantuan Login")

    def _check_google_profile(self, profile_id: str) -> None:
        if self._google_session_service is None:
            return
        self._invalidate_google_flow(profile_id)
        future = self._google_session_service.check_profile_async(profile_id)
        self._watch_google_profile_future(future, "check", "Profil Google")

    def _check_all_google_profiles(self) -> None:
        if self._google_session_service is None:
            return
        for profile in self._google_session_service.list_profiles():
            self._invalidate_google_flow(profile.profile_id)
        future = self._google_session_service.check_all_async()
        self._watch_google_all_future(future, "Profil Google")

    def _invalidate_google_flow(self, profile_id: str) -> int:
        """Revoke cached Flow proof and fence callbacks after session changes."""

        self._google_flow_probes.pop(profile_id, None)
        self._google_flow_busy.discard(profile_id)
        epoch = self._google_flow_epochs.get(profile_id, 0) + 1
        self._google_flow_epochs[profile_id] = epoch
        return epoch

    def _check_active_google_flow(self) -> None:
        """Run read-only Flow preflight without blocking Qt or mutating Flow."""

        sessions = self._google_session_service
        preflight = self._google_flow_preflight_service
        profile_id = self._active_google_profile_id
        if sessions is None or preflight is None or profile_id is None:
            return
        if profile_id in self._google_flow_busy:
            return
        if sessions.get_restart_gate(profile_id).current_state is not GoogleSessionState.READY:
            QMessageBox.warning(self, "Cek Akses Flow", "Cek Ulang Sesi Google terlebih dahulu.")
            return

        epoch = self._invalidate_google_flow(profile_id)
        self._google_flow_busy.add(profile_id)
        current_profile = next(
            (p for p in sessions.list_profiles() if p.profile_id == profile_id),
            None,
        )
        if current_profile is not None:
            self.show_google_login(current_profile)
        future = preflight.check_async(profile_id)

        def completed(done: Future[GoogleFlowAccessProbe]) -> None:
            if self._google_browser_closed:
                return
            try:
                probe = done.result()
            except FlowOtomatisError as exc:
                self._google_flow_signals.failed.emit(profile_id, epoch, str(exc))
            except Exception:
                self._google_flow_signals.failed.emit(
                    profile_id, epoch, "Pemeriksaan Flow gagal tanpa data akun sensitif."
                )
            else:
                self._google_flow_signals.checked.emit(profile_id, epoch, probe)

        future.add_done_callback(completed)

    def _on_google_flow_checked(
        self,
        requested_profile_id: str,
        epoch: int,
        probe: GoogleFlowAccessProbe,
    ) -> None:
        if self._google_browser_closed:
            return
        if self._google_flow_epochs.get(requested_profile_id) != epoch:
            return
        if probe.profile_id != requested_profile_id:
            # Never permit a response for profile B to authorize profile A.
            self._google_flow_busy.discard(requested_profile_id)
            self._refresh_active_google_login(requested_profile_id)
            return
        if self._google_session_service is None:
            return
        if probe.profile_id not in {
            p.profile_id for p in self._google_session_service.list_profiles()
        }:
            return
        self._google_flow_busy.discard(probe.profile_id)
        self._google_flow_probes[probe.profile_id] = probe
        self._refresh_active_google_login(probe.profile_id)

    def _on_google_flow_failed(self, profile_id: str, epoch: int, detail: str) -> None:
        if self._google_browser_closed or self._google_flow_epochs.get(profile_id) != epoch:
            return
        self._google_flow_busy.discard(profile_id)
        self._refresh_active_google_login(profile_id)
        if (
            self._fixture_code == "REAL_GOOGLE_LOGIN"
            and self._active_google_profile_id == profile_id
        ):
            QMessageBox.warning(self, "Cek Akses Flow", detail)

    def _refresh_active_google_login(self, profile_id: str) -> None:
        if (
            self._google_session_service is None
            or self._fixture_code != "REAL_GOOGLE_LOGIN"
            or self._active_google_profile_id != profile_id
        ):
            return
        profile = next(
            (p for p in self._google_session_service.list_profiles() if p.profile_id == profile_id),
            None,
        )
        if profile is not None:
            self.show_google_login(profile)

    def _watch_google_profile_future(
        self,
        future: Future[GoogleSessionProfile],
        action: str,
        title: str,
    ) -> None:
        """Observe only sanitized DTOs; worker callbacks emit Qt signals."""

        def completed(done: Future[GoogleSessionProfile]) -> None:
            try:
                profile = done.result()
            except FlowOtomatisError as exc:
                self._google_session_signals.failed.emit(title, str(exc))
            except Exception:
                self._google_session_signals.failed.emit(
                    title,
                    "Operasi sesi Google gagal tanpa mengekspos detail browser.",
                )
            else:
                self._google_session_signals.profile_ready.emit(action, profile)

        future.add_done_callback(completed)

    def _watch_google_all_future(
        self,
        future: Future[tuple[GoogleSessionProfile, ...]],
        title: str,
    ) -> None:
        def completed(done: Future[tuple[GoogleSessionProfile, ...]]) -> None:
            try:
                done.result()
            except FlowOtomatisError as exc:
                self._google_session_signals.failed.emit(title, str(exc))
            except Exception:
                self._google_session_signals.failed.emit(
                    title,
                    "Operasi sesi Google gagal tanpa mengekspos detail browser.",
                )
            else:
                self._google_session_signals.all_ready.emit()

        future.add_done_callback(completed)

    def _on_google_session_profile_ready(
        self,
        action: str,
        profile: GoogleSessionProfile,
    ) -> None:
        if self._google_browser_closed:
            return
        if action == "open":
            self.show_google_login(profile)
            return
        if action == "recheck":
            if self._active_google_profile_id == profile.profile_id:
                self.show_google_login(profile)
            return
        if self._fixture_code == "REAL_GOOGLE_PROFILES":
            self.show_google_profiles()

    def _show_google_session_error(self, title: str, message: str) -> None:
        if not self._google_browser_closed:
            QMessageBox.warning(self, title, message)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Bound how long Qt waits while Browser Worker cleans up."""

        self._agent_closed = True
        self._google_browser_closed = True
        for profile_id in tuple(self._google_flow_epochs):
            self._invalidate_google_flow(profile_id)
        self._invalidate_agent_context()
        if self._google_session_service is not None:
            self._google_session_service.shutdown(timeout_s=1.5)
        super().closeEvent(event)

    def _wire_import_button(self, screen: QWidget) -> None:
        if self._episode_import_service is None:
            return
        for button in screen.findChildren(QPushButton):
            if button.text() == "Impor Paket Episode":
                button.clicked.connect(self._choose_episode_package)
                return

    def _choose_episode_package(self, checked: bool = False) -> None:
        del checked
        filename, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Impor Paket Episode",
            "",
            "Episode Package (*.zip);;Flow Manifest (FLOW_OTOMATIS_IMPORT.json *.json)",
        )
        if not filename:
            return
        try:
            self.import_episode_package(Path(filename))
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Paket Episode Tidak Valid", str(exc))

    def import_episode_package(self, source_path: Path) -> WorkspaceState:
        """Validate a selected package and render real validation state."""

        if self._episode_import_service is None:
            raise InternalInvariantError("Episode import service is not configured")
        workspace = self._episode_import_service.validate(source_path)
        self._invalidate_agent_context()
        self._pending_workspace = workspace
        self._fixture_code = "REAL_VALIDATION"
        self._set_navigation("Workspace")
        self._set_project_chrome(workspace, "Validasi Paket Episode")
        view = build_validation_view(
            workspace,
            on_create=self._create_pending_workspace_from_ui,
            on_cancel=self.show_project_hub,
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)
        return workspace

    def _create_pending_workspace_from_ui(self) -> None:
        """Create from the Qt button and translate typed persistence errors safely."""

        try:
            self.create_pending_workspace()
        except WorkspaceAlreadyExistsError as exc:
            QMessageBox.warning(
                self,
                "Project Sudah Ada",
                (
                    f"Episode {exc.episode_id} sudah pernah diimpor. "
                    "Buka project yang sudah ada dari Beranda."
                ),
            )
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Workspace Tidak Dapat Dibuat", str(exc))

    def create_pending_workspace(self) -> WorkspaceState:
        """Persist the currently validated package and render real workspace rows."""

        if self._episode_import_service is None:
            raise InternalInvariantError("Episode import service is not configured")
        if self._pending_workspace is None:
            raise InternalInvariantError("No validated package is waiting to be created")
        workspace = self._episode_import_service.create_workspace(self._pending_workspace)
        self._pending_workspace = None
        self._current_workspace = workspace
        self._selected_scene_id = workspace.scenes[0].scene_id if workspace.scenes else None
        self.show_workspace_state(workspace)
        return workspace

    def show_workspace_state(self, workspace: WorkspaceState) -> None:
        """Render frozen Workspace/Scene Inspector from persisted real state."""

        self._invalidate_agent_context()
        self._fixture_code = "REAL_WORKSPACE"
        self._current_workspace = workspace
        if workspace.scenes and self._selected_scene_id not in {
            scene.scene_id for scene in workspace.scenes
        }:
            self._selected_scene_id = workspace.scenes[0].scene_id

        self._set_navigation("Workspace")
        self._set_project_chrome(workspace, "Workspace")
        view = build_workspace_view(
            workspace,
            on_rescan_images=self.rescan_workspace_images,
            on_scene_selected=self.select_workspace_scene,
            on_preview_credit_ui=self.open_credit_uix_preview,
            on_local_preflight=self.open_local_scene_preflight,
            on_bulk_durations=self.auto_fill_scene_durations,
            selected_scene_id=self._selected_scene_id,
        )
        self._replace_layout_widget(self._content_layout, view)
        self._render_workspace_right_panel()

    def auto_fill_scene_durations(self) -> WorkspaceState | None:
        """Preview and explicitly confirm one safe bulk local duration update."""
        if self._fixture_code != "REAL_WORKSPACE" or self._current_workspace is None:
            return None
        if self._scene_planning_service is None:
            raise InternalInvariantError("Scene planning service is not configured")
        episode_id = self._current_workspace.episode_id
        try:
            snapshot = self._scene_planning_service.load_workspace(episode_id)
            plan = self._scene_planning_service.preview_missing_recommended_durations(episode_id)
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Rencana Durasi Tidak Tersedia", str(exc))
            return None
        if not plan:
            QMessageBox.information(
                self,
                "Tidak Ada Durasi yang Perlu Diisi",
                "Semua durasi sudah dipilih, atau ada Target yang perlu diperbaiki manual.",
            )
            return None
        distribution = dict.fromkeys((4, 6, 8, 10), 0)
        for _scene_id, duration in plan:
            distribution[duration] += 1
        breakdown = " • ".join(
            f"{duration}s: {distribution[duration]}" for duration in (4, 6, 8, 10)
        )
        confirm = QMessageBox.question(
            self,
            "Konfirmasi Durasi Flow Massal",
            f"Isi durasi rekomendasi untuk {len(plan)} Scene yang belum dipilih?\n"
            f"{breakdown}\n\n"
            "Pilihan manual, target narasi, dan checksum gambar tetap sama. "
            "Tidak membuat antrean atau menjalankan Google Flow.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return None
        if (
            self._fixture_code != "REAL_WORKSPACE"
            or self._current_workspace is None
            or self._current_workspace.episode_id != episode_id
        ):
            return None
        try:
            workspace = self._scene_planning_service.fill_missing_recommended_durations(
                episode_id, expected_workspace=snapshot
            )
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Tidak Dapat Mengisi Durasi", str(exc))
            # Display current durable state rather than a stale planning table.
            latest = self._scene_planning_service.load_workspace(episode_id)
            if (
                self._current_workspace is not None
                and self._current_workspace.episode_id == episode_id
            ):
                self.show_workspace_state(latest)
            return None
        self.show_workspace_state(workspace)
        return workspace

    def open_local_scene_preflight(self) -> None:
        """Audit real Workspace Scene metadata; do not touch durable generation jobs."""
        workspace = self._current_workspace
        if workspace is None or self._fixture_code != "REAL_WORKSPACE":
            return
        dialog = LocalScenePreflightDialog(
            workspace, parent=self, image_verifier=self._image_verifier
        )
        dialog.exec()
        self._return_to_local_scene(workspace, dialog.requested_scene_id)

    def _return_to_local_scene(
        self, workspace: WorkspaceState, requested_scene_id: str | None
    ) -> None:
        """Return only to a unique Scene in the exact currently opened Workspace."""
        if requested_scene_id is None:
            return
        if self._current_workspace is not workspace or self._fixture_code != "REAL_WORKSPACE":
            return
        if sum(scene.scene_id == requested_scene_id for scene in workspace.scenes) != 1:
            return
        self._selected_scene_id = requested_scene_id
        self.show_workspace_state(workspace)

    def open_credit_uix_preview(self) -> None:
        """Show 22 offline-only UI states as a REAL page in the main Qt shell."""

        if self._active_uix_preview is not None:
            # Repeated clicks cannot stack a second modal/preview route.
            return
        self._invalidate_agent_context()
        workspace = self._current_workspace if self._fixture_code == "REAL_WORKSPACE" else None
        preview = CreditUixDialog(
            self,
            workspace=workspace,
            image_verifier=self._image_verifier,
            default_to_demo=True,
            app_shell=True,
        )
        # QDialog inherits QWidget; embedding it avoids another top-level
        # window and a second copy of the approved main-app navigation.
        preview.setWindowFlags(Qt.WindowType.Widget)
        preview.finished.connect(lambda _result: self._return_from_uix_preview(preview))
        self._fixture_code = "REAL_UIX22_PREVIEW"
        self._set_navigation("Workspace")
        self._project_state_label.setText("UIX22 • Simulasi")
        self._status_project.setText("22 kondisi UI • Tanpa Generate")
        self._uix_return_workspace = workspace
        self._active_uix_preview = preview
        self._replace_layout_widget(self._content_layout, preview)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)
        preview.show()

    def _return_from_uix_preview(self, preview: CreditUixDialog) -> None:
        """Return safely to the originating local workspace or real Beranda."""

        if self._active_uix_preview is not preview:
            return
        workspace = self._uix_return_workspace
        chosen_scene = preview.requested_scene_id
        self._active_uix_preview = None
        self._uix_return_workspace = None
        if workspace is None or self._current_workspace is not workspace:
            self.show_project_hub()
            return
        if (
            chosen_scene is not None
            and sum(scene.scene_id == chosen_scene for scene in workspace.scenes) == 1
        ):
            self._selected_scene_id = chosen_scene
        self.show_workspace_state(workspace)

    def select_workspace_scene(self, scene_id: str) -> None:
        """Select only a persisted Scene row and refresh the Scene Inspector."""

        if (
            self._fixture_code != "REAL_WORKSPACE"
            or self._current_workspace is None
            or not any(scene.scene_id == scene_id for scene in self._current_workspace.scenes)
        ):
            return
        self._invalidate_agent_context()
        self._selected_scene_id = scene_id
        self._render_workspace_right_panel()

    def select_scene_duration(self, duration_s: int) -> WorkspaceState:
        """Persist a valid Flow duration selection for the active Scene."""

        if self._scene_planning_service is None:
            raise InternalInvariantError("Scene planning service is not configured")
        if self._current_workspace is None or self._selected_scene_id is None:
            raise InternalInvariantError("No active workspace Scene")
        try:
            workspace = self._scene_planning_service.select_flow_duration(
                self._current_workspace.episode_id,
                self._selected_scene_id,
                duration_s,
            )
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Durasi Flow Tidak Valid", str(exc))
            raise
        self.show_workspace_state(workspace)
        return workspace

    def rescan_workspace_images(self) -> WorkspaceState:
        """Rescan approved images through the application service and refresh UI."""

        if self._scene_planning_service is None:
            raise InternalInvariantError("Scene planning service is not configured")
        if self._current_workspace is None:
            raise InternalInvariantError("No active workspace")
        try:
            workspace = self._scene_planning_service.rescan_images(
                self._current_workspace.episode_id
            )
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Scan Gambar Ditolak", str(exc))
            return self._current_workspace
        self.show_workspace_state(workspace)
        return workspace

    def _invalidate_agent_context(self) -> None:
        """Retire all previous completions when visible context changes."""

        self._agent_context_generation += 1
        self._active_agent_request = None
        self._agent_busy = False
        self._agent_answer = None

    def _is_current_agent_request(self, request: _GeminiAgentRequest) -> bool:
        return (
            not self._agent_closed
            and self._fixture_code == "REAL_WORKSPACE"
            and self._active_agent_request == request
            and self._agent_context_generation == request.context_generation
            and self._current_workspace is not None
            and self._current_workspace.episode_id == request.episode_id
            and self._selected_scene_id == request.scene_id
        )

    def _ask_gemini_agent(self, question: str) -> None:
        if self._gemini_agent_service is None:
            self._agent_answer = (
                "AI Agent belum dikonfigurasi. "
                "Tambahkan dan health-check Gemini key terlebih dahulu."
            )
            self._render_workspace_right_panel()
            return
        if self._current_workspace is None or self._selected_scene_id is None:
            return
        if self._agent_busy or self._agent_closed:
            return

        self._agent_request_id += 1
        request = _GeminiAgentRequest(
            request_id=self._agent_request_id,
            episode_id=self._current_workspace.episode_id,
            scene_id=self._selected_scene_id,
            context_generation=self._agent_context_generation,
        )
        self._active_agent_request = request
        self._agent_busy = True
        self._agent_answer = None
        self._render_workspace_right_panel()

        # Keep the bridge alive with its QRunnable rather than parent it to the window:
        # a closing window must never destroy a signal emitter used by a worker.
        signals = _GeminiAgentSignals()
        signals.answered.connect(self._on_gemini_agent_answered)
        signals.failed.connect(self._on_gemini_agent_failed)
        task = _GeminiAgentTask(
            self._gemini_agent_service,
            self._current_workspace,
            self._selected_scene_id,
            question,
            request,
            signals,
        )
        QThreadPool.globalInstance().start(task)

    def _on_gemini_agent_answered(
        self, request: _GeminiAgentRequest, reply: GeminiAgentReply
    ) -> None:
        if not self._is_current_agent_request(request):
            return
        self._active_agent_request = None
        self._agent_busy = False
        self._agent_answer = reply.text
        self._render_workspace_right_panel()

    def _on_gemini_agent_failed(self, request: _GeminiAgentRequest, message: str) -> None:
        if not self._is_current_agent_request(request):
            return
        self._active_agent_request = None
        self._agent_busy = False
        self._agent_answer = f"AI Agent belum bisa menjawab: {message}"
        self._render_workspace_right_panel()

    def _render_workspace_right_panel(self) -> None:
        if self._current_workspace is None or not self._current_workspace.scenes:
            self._replace_layout_widget(self._right_layout, None)
            self._right_host.setVisible(False)
            return
        scene_id = self._selected_scene_id or self._current_workspace.scenes[0].scene_id
        right_panel = build_workspace_right_panel(
            self._current_workspace,
            scene_id=scene_id,
            on_select_duration=self.select_scene_duration,
            on_agent_question=self._ask_gemini_agent,
            agent_answer=self._agent_answer,
            agent_busy=self._agent_busy,
        )
        self._replace_layout_widget(self._right_layout, right_panel)
        self._right_host.setVisible(right_panel is not None)
