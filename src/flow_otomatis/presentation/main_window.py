"""Production application shell for the frozen STEP 09 UI."""

from __future__ import annotations

from functools import partial
from pathlib import Path

from PySide6.QtCore import Qt
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

from flow_otomatis.application.ports import GoogleSessionProfile
from flow_otomatis.application.services import (
    EpisodeImportService,
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
from flow_otomatis.domain.project import WorkspaceState
from flow_otomatis.presentation.fixtures import (
    DEFAULT_FIXTURE_CODE,
    NAV_ITEMS,
    get_fixture,
)
from flow_otomatis.presentation.google_profiles_view import (
    build_google_login_view,
    build_google_profiles_view,
)
from flow_otomatis.presentation.project_hub_view import build_project_hub_view
from flow_otomatis.presentation.results_view import build_results_view
from flow_otomatis.presentation.screen_factory import build_right_panel, build_screen
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
        project_library_service: ProjectLibraryService | None = None,
        local_results_service: LocalResultsService | None = None,
        google_session_service: GoogleSessionService | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Flow-Otomatis")
        self.setObjectName("FlowOtomatisMainWindow")
        self.setStyleSheet(application_stylesheet())
        self.resize(1600, 900)
        self.setMinimumSize(1180, 700)

        self._fixture_code = fixture_code
        self._nav_buttons: dict[str, QPushButton] = {}
        self._episode_import_service = episode_import_service
        self._scene_planning_service = scene_planning_service
        self._project_library_service = project_library_service
        self._local_results_service = local_results_service
        self._google_session_service = google_session_service
        self._active_google_profile_id: str | None = None
        self._last_result_manifest_path: Path | None = None
        self._pending_workspace: WorkspaceState | None = None
        self._current_workspace: WorkspaceState | None = None
        self._selected_scene_id: str | None = None

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
            item == "Hasil"
            and self._current_workspace is not None
            and self._local_results_service is not None
        ):
            self.show_results_state()
            return
        if item == "Profil Google" and self._google_session_service is not None:
            self.show_google_profiles()
            return
        self.show_fixture(_NAV_DEFAULTS[item])

    def _replace_layout_widget(self, layout: QVBoxLayout, widget: QWidget | None) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                break
            old_widget = item.widget()
            if old_widget is not None:
                old_widget.setParent(None)
                old_widget.deleteLater()
        if widget is not None:
            layout.addWidget(widget)

    def _set_navigation(self, item: str) -> None:
        for name, button in self._nav_buttons.items():
            button.setChecked(name == item)

    def _set_project_chrome(self, workspace: WorkspaceState, surface: str) -> None:
        self._project_label.setText(f"{workspace.episode_id} • {workspace.project_name}")
        self._project_state_label.setText(surface)
        self._status_project.setText(f"{workspace.episode_id} • {len(workspace.scenes)} scene")

    def show_fixture(self, code: str) -> None:
        """Render one approved visual state inside the production shell."""

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

        screen = build_screen(fixture)
        self._replace_layout_widget(self._content_layout, screen)
        right_panel = build_right_panel(fixture)
        self._replace_layout_widget(self._right_layout, right_panel)
        self._right_host.setVisible(right_panel is not None)
        self._wire_import_button(screen)

    def show_project_hub(self) -> None:
        """Render real local recent projects using the frozen Project Hub."""

        if self._project_library_service is None:
            self.show_fixture("UI-IMG-001A")
            return
        scan = self._project_library_service.scan_recent()
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
        )
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
                (
                    f"Project {episode_id} sementara tidak dapat dibaca. "
                    "File project tidak diubah."
                ),
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
        self._fixture_code = "REAL_RESULTS"
        self._set_navigation("Hasil")
        self._set_project_chrome(self._current_workspace, "Hasil")
        view = build_results_view(
            results,
            on_export_manifest=self.export_current_result_manifest,
        )
        self._replace_layout_widget(self._content_layout, view)
        self._replace_layout_widget(self._right_layout, None)
        self._right_host.setVisible(False)

    def export_current_result_manifest(self) -> Path:
        """Export the current credential-free FLOW_OTOMATIS_RESULT.json."""

        if self._local_results_service is None:
            raise InternalInvariantError("Local results service is not configured")
        if self._current_workspace is None:
            raise InternalInvariantError("No active workspace")
        path = self._local_results_service.export_manifest(self._current_workspace.episode_id)
        self._last_result_manifest_path = path
        return path

    def show_google_profiles(self) -> None:
        """Render real credential-free Google profile/session state."""

        if self._google_session_service is None:
            self.show_fixture("UI-IMG-004A")
            return
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
        try:
            profile = self._google_session_service.open_login(profile_id)
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Bantuan Login", str(exc))
            return
        self.show_google_login(profile)

    def _reopen_active_google_login(self) -> None:
        if self._active_google_profile_id is None:
            self.show_google_profiles()
            return
        self._open_google_login(self._active_google_profile_id)

    def _recheck_active_google_login(self) -> None:
        if self._google_session_service is None or self._active_google_profile_id is None:
            self.show_google_profiles()
            return
        try:
            profile = self._google_session_service.check_profile(self._active_google_profile_id)
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Bantuan Login", str(exc))
            return
        self.show_google_login(profile)

    def _check_google_profile(self, profile_id: str) -> None:
        if self._google_session_service is None:
            return
        try:
            self._google_session_service.check_profile(profile_id)
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Profil Google", str(exc))
            return
        self.show_google_profiles()

    def _check_all_google_profiles(self) -> None:
        if self._google_session_service is None:
            return
        try:
            self._google_session_service.check_all()
        except FlowOtomatisError as exc:
            QMessageBox.warning(self, "Profil Google", str(exc))
            return
        self.show_google_profiles()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Close Browser Worker resources before the Qt shell exits."""

        if self._google_session_service is not None:
            self._google_session_service.shutdown()
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
        )
        self._replace_layout_widget(self._content_layout, view)
        self._render_workspace_right_panel()

    def select_workspace_scene(self, scene_id: str) -> None:
        """Select a real Scene row and refresh only the Scene Inspector."""

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
        workspace = self._scene_planning_service.rescan_images(self._current_workspace.episode_id)
        self.show_workspace_state(workspace)
        return workspace

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
        )
        self._replace_layout_widget(self._right_layout, right_panel)
        self._right_host.setVisible(right_panel is not None)
