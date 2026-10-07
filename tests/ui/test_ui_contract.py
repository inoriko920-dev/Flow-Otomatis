from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTableWidget

from flow_otomatis.presentation.fixtures import FIXTURE_CODES, NAV_ITEMS
from flow_otomatis.presentation.main_window import MainWindow


def _visible_text(window: MainWindow) -> str:
    parts = [label.text() for label in window.findChildren(QLabel)]
    for table in window.findChildren(QTableWidget):
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None:
                    parts.append(item.text())
    return "\n".join(parts)


def test_fixture_registry_contains_all_30_frozen_states() -> None:
    assert len(FIXTURE_CODES) == 30
    assert len(set(FIXTURE_CODES)) == 30
    assert FIXTURE_CODES[0] == "UI-IMG-001A"
    assert FIXTURE_CODES[-1] == "UI-IMG-015A"


def test_global_sidebar_does_not_promote_recovery_center() -> None:
    assert NAV_ITEMS == (
        "Beranda",
        "Workspace",
        "Hasil",
        "Profil Google",
        "Gemini Keys",
        "Diagnostik",
        "Pengaturan",
    )
    assert "Recovery Center" not in NAV_ITEMS


def test_all_frozen_fixtures_render(qtbot: object) -> None:
    del qtbot
    window = MainWindow()
    try:
        for code in FIXTURE_CODES:
            window.show_fixture(code)
            assert window.fixture_code == code
            assert window.centralWidget() is not None
    finally:
        window.close()


def test_production_lock_copy_matches_override(qtbot: object) -> None:
    del qtbot
    window = MainWindow("UI-IMG-007A")
    try:
        text = _visible_text(window)
        assert "Omni Flash 1.1" in text
        assert "720p" in text
        assert "16:9" in text
        assert "72:9" not in text
    finally:
        window.close()


def test_handoff_uses_video_output_semantics(qtbot: object) -> None:
    del qtbot
    window = MainWindow("UI-IMG-003C")
    try:
        text = _visible_text(window)
        assert ".mp4" in text
        assert "video generated" in text
        assert "video downloaded" in text
    finally:
        window.close()


def test_diagnostics_forbids_automatic_ai_retry(qtbot: object) -> None:
    del qtbot
    window = MainWindow("UI-IMG-008A")
    try:
        text = _visible_text(window)
        assert "tidak melakukan retry otomatis" in text
        assert "ditinjau dan disetujui pengguna" in text
    finally:
        window.close()


def test_scene_inspector_preserves_target_and_valid_flow_choices(qtbot: object) -> None:
    del qtbot
    window = MainWindow("UI-IMG-011A")
    try:
        text = _visible_text(window)
        assert "7.32s" in text
        assert "8s" in text
        assert "Omni Flash 1.1" in text
    finally:
        window.close()
