"""The live Beranda must not expose inert project actions or false data."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget

from flow_otomatis.presentation.fixtures import get_fixture
from flow_otomatis.presentation.main_window import MainWindow
from flow_otomatis.presentation.project_hub_view import build_project_hub_view
from flow_otomatis.presentation.screen_factory import build_screen


def _button(root, object_name: str) -> QPushButton:
    button = root.findChild(QPushButton, object_name)
    assert button is not None
    return button


def test_empty_hub_with_unavailable_import_disables_inert_actions(qtbot) -> None:
    """Only supported operations are clickable if no local project exists."""

    window = MainWindow(
        project_library_service=SimpleNamespace(
            scan_recent=lambda: SimpleNamespace(workspaces=(), issues=())
        )
    )
    qtbot.addWidget(window)
    window.configure_production_shell()
    window.show_project_hub()
    page = window._content_layout.itemAt(0).widget()
    assert page is not None
    assert window.fixture_code == "REAL_PROJECT_HUB"

    open_project = _button(page, "ProjectHubOpenProject")
    create_project = _button(page, "ProjectHubCreateFromPackage")
    assert open_project.text() == "Buka Project"
    assert not open_project.isEnabled()
    assert "Belum ada project" in open_project.toolTip()
    assert create_project.text() == "Buat Project dari Paket"
    assert not create_project.isEnabled()

    import_button = next(
        button
        for button in page.findChildren(QPushButton)
        if button.text() == "Impor Paket Episode"
    )
    assert not import_button.isEnabled()
    assert "belum tersedia" in import_button.toolTip()
    text = " ".join(label.text() for label in page.findChildren(QLabel))
    assert "Project tersimpan akan muncul" in text
    assert "EP001 Steve Jobs" not in text
    window.close()


def test_empty_hub_create_and_import_both_call_real_package_dialog(qtbot, monkeypatch) -> None:
    """Creating a project requires a package, never an unpersisted empty record."""

    window = MainWindow(
        project_library_service=SimpleNamespace(
            scan_recent=lambda: SimpleNamespace(workspaces=(), issues=())
        ),
        episode_import_service=object(),
    )
    qtbot.addWidget(window)
    window.configure_production_shell()
    calls: list[str] = []
    monkeypatch.setattr(window, "_choose_episode_package", lambda: calls.append("import"))
    window.show_project_hub()

    page = window._content_layout.itemAt(0).widget()
    assert page is not None
    create_project = _button(page, "ProjectHubCreateFromPackage")
    import_button = next(
        button
        for button in page.findChildren(QPushButton)
        if button.text() == "Impor Paket Episode"
    )
    assert create_project.isEnabled() and import_button.isEnabled()
    create_project.click()
    import_button.click()
    assert calls == ["import", "import"]
    assert not _button(page, "ProjectHubOpenProject").isEnabled()
    window.close()


def test_populated_hub_has_working_open_and_create_shortcuts(qtbot) -> None:
    """Existing local project can open; create still uses real import."""

    saved = SimpleNamespace(
        project_name="Real Saved Project",
        episode_id="EP_SAFE_17",
        scenes=(object(),),
        blocking_count=0,
        duration_selection_count=0,
        imported_at=datetime.now(UTC),
    )
    opened: list[str] = []
    imported: list[str] = []
    root = build_project_hub_view(
        (saved,),
        on_open=lambda eid: opened.append(eid),
        on_import=lambda: imported.append("import"),
        import_available=True,
    )
    qtbot.addWidget(root)
    assert _button(root, "ProjectHubOpenProject").isEnabled()
    _button(root, "ProjectHubOpenProject").click()
    _button(root, "ProjectHubCreateFromPackage").click()
    assert opened == ["EP_SAFE_17"]
    assert imported == ["import"]
    table = next(t for t in root.findChildren(QTableWidget) if t.columnCount() == 5)
    assert table.item(0, 0).text() == "Real Saved Project"
    root.close()


def test_original_frozen_project_hub_buttons_are_not_modified(qtbot) -> None:
    """Owner-approved source screenshot must still show its original controls."""

    root = build_screen(get_fixture("UI-IMG-001A"))
    qtbot.addWidget(root)
    buttons = [b.text() for b in root.findChildren(QPushButton)]
    assert "Impor Paket Episode" in buttons
    assert "Buat Project" in buttons
    assert "Buka Project" in buttons
    assert "Buat Project dari Paket" not in buttons
    root.close()
