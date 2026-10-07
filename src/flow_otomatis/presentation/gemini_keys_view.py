"""Bind real Gemini key metadata to the frozen STEP 09 keys screen."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtWidgets import QPushButton, QTableWidget, QTableWidgetItem, QWidget

from flow_otomatis.domain.gemini import GeminiKeyProfile, GeminiKeyStatus
from flow_otomatis.presentation.fixtures import get_fixture
from flow_otomatis.presentation.screen_factory import build_screen


def _keys_table(root: QWidget) -> QTableWidget:
    for table in root.findChildren(QTableWidget):
        if table.columnCount() == 5:
            return table
    raise RuntimeError("Frozen Gemini Keys view is missing its five-column table")


def _button(root: QWidget, text: str) -> QPushButton | None:
    return next((button for button in root.findChildren(QPushButton) if button.text() == text), None)


def _status_text(status: GeminiKeyStatus) -> str:
    return {
        GeminiKeyStatus.UNCHECKED: "Belum dicek",
        GeminiKeyStatus.VALID: "Valid",
        GeminiKeyStatus.INVALID: "Ditolak",
        GeminiKeyStatus.ERROR: "Error",
    }[status]


def build_gemini_keys_view(
    profiles: Sequence[GeminiKeyProfile],
    *,
    on_import: Callable[[], object],
    on_check: Callable[[str], object],
    on_activate: Callable[[str], object],
) -> QWidget:
    """Render credential-free key metadata without ever showing a raw key."""

    root = build_screen(get_fixture("UI-IMG-006A"))
    table = _keys_table(root)
    table.setRowCount(len(profiles))
    key_ids: list[str] = []

    for row, profile in enumerate(profiles):
        key_ids.append(profile.key_id)
        checked = (
            profile.last_checked_at.astimezone().strftime("%H:%M")
            if profile.last_checked_at is not None
            else "—"
        )
        values = (
            profile.label,
            profile.masked_key,
            _status_text(profile.status),
            checked,
            "AI Agent" if profile.is_active else "Tidak aktif",
        )
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(value))

    if profiles:
        table.setCurrentCell(0, 0)

    import_button = _button(root, "Impor TXT / Paste")
    if import_button is not None:
        import_button.clicked.connect(on_import)

    check_button = _button(root, "Cek Health")
    if check_button is not None:
        check_button.clicked.connect(
            lambda: on_check(key_ids[table.currentRow()])
            if 0 <= table.currentRow() < len(key_ids)
            else None
        )

    table.cellDoubleClicked.connect(
        lambda row, _column: on_activate(key_ids[row]) if 0 <= row < len(key_ids) else None
    )
    return root
