"""Production empty Workspace/Hasil must not masquerade as completed scenes."""

from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from flow_otomatis.presentation.main_window import MainWindow


class EmptyLibrary:
    def scan_recent(self):
        return SimpleNamespace(workspaces=(), issues=())


def _visible_page_text(window: MainWindow) -> str:
    page = window._content_layout.itemAt(0).widget()
    assert page is not None
    return " ".join(label.text() for label in page.findChildren(QLabel))


def test_workspace_without_project_has_real_empty_state_and_back_to_hub(qtbot) -> None:
    window = MainWindow(project_library_service=EmptyLibrary())
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Workspace")

    assert window.fixture_code == "REAL_EMPTY_WORKSPACE"
    page = window._content_layout.itemAt(0).widget()
    assert isinstance(page, QWidget)
    assert page.objectName() == "RealEmptyWorkspace"
    assert window._nav_buttons["Workspace"].isChecked()
    assert "Belum ada Workspace aktif" in _visible_page_text(window)
    assert "TIDAK ADA PROJECT AKTIF" in _visible_page_text(window)
    assert "EP001" not in _visible_page_text(window)
    assert "60 scene" not in _visible_page_text(window)
    assert window._connection_badge.text() == "●  Mode Lokal"
    assert window._right_host.isHidden()
    import_button = page.findChild(QPushButton, "RealEmptyImport")
    assert import_button is not None and not import_button.isEnabled()
    assert "Layanan impor paket" in import_button.toolTip()
    home = page.findChild(QPushButton, "RealEmptyHome")
    assert home is not None and home.isEnabled()
    home.click()
    assert window.fixture_code == "REAL_PROJECT_HUB"
    assert window._nav_buttons["Beranda"].isChecked()
    window.close()


def test_results_without_project_never_shows_demo_mp4_or_generate_history(qtbot) -> None:
    window = MainWindow(project_library_service=EmptyLibrary())
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Hasil")

    assert window.fixture_code == "REAL_EMPTY_HASIL"
    assert window._nav_buttons["Hasil"].isChecked()
    assert "Belum ada hasil proyek" in _visible_page_text(window)
    assert "Belum ada video untuk diunduh" in _visible_page_text(window)
    assert "Tidak ada project dipilih" in window._project_label.text()
    assert "MP4 simulasi tidak digunakan" in _visible_page_text(window)
    assert "Download Selesai" not in _visible_page_text(window)
    assert "EP001" not in _visible_page_text(window)
    assert window._right_host.isHidden()
    window.close()


def test_empty_page_import_button_is_wired_only_if_service_is_available(qtbot, monkeypatch) -> None:
    window = MainWindow(
        project_library_service=EmptyLibrary(),
        episode_import_service=object(),
    )
    qtbot.addWidget(window)
    window.configure_production_shell()
    calls: list[str] = []
    monkeypatch.setattr(window, "_choose_episode_package", lambda: calls.append("import"))
    window._open_navigation_item("Workspace")

    page = window._content_layout.itemAt(0).widget()
    assert page is not None
    button = page.findChild(QPushButton, "RealEmptyImport")
    assert button is not None and button.isEnabled()
    button.click()
    assert calls == ["import"]
    assert window.fixture_code == "REAL_EMPTY_WORKSPACE"
    window.close()


def test_switching_empty_routes_preserves_navigation_and_no_provider_use(qtbot) -> None:
    window = MainWindow(project_library_service=EmptyLibrary())
    qtbot.addWidget(window)
    window.configure_production_shell()
    window._open_navigation_item("Hasil")
    window._open_navigation_item("Workspace")
    assert window.fixture_code == "REAL_EMPTY_WORKSPACE"
    assert window._nav_buttons["Workspace"].isChecked()
    assert window._connection_badge.text() == "●  Mode Lokal"
    assert window._runtime_status.text() == "Mode lokal • Generate Flow belum aktif"
    window.close()


def test_explicit_fixture_routes_keep_the_approved_static_screens(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._open_navigation_item("Workspace")
    assert window.fixture_code == "UI-IMG-002A"
    window._open_navigation_item("Hasil")
    assert window.fixture_code == "UI-IMG-003A"
    assert window._content_layout.itemAt(0).widget().objectName() != "RealEmptyHasil"
    window.close()
