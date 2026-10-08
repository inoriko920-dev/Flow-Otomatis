from __future__ import annotations

from pathlib import Path
from threading import Event


from PySide6.QtWidgets import QTableWidget

from flow_otomatis.application.ports.gemini_keys import GeminiKeyHealthEvidence
from flow_otomatis.application.services.gemini_keys import GeminiKeyService
from flow_otomatis.domain.gemini import GeminiKeyStatus
from flow_otomatis.infrastructure.persistence import SqliteGeminiKeyRepository
from flow_otomatis.presentation.main_window import MainWindow


class MemorySecrets:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def set_secret(self, key_id: str, secret: str) -> None:
        self.values[key_id] = secret

    def get_secret(self, key_id: str) -> str | None:
        return self.values.get(key_id)

    def delete_secret(self, key_id: str) -> None:
        self.values.pop(key_id, None)


class ValidHealth:
    def check(self, api_key: str) -> GeminiKeyHealthEvidence:
        assert api_key
        return GeminiKeyHealthEvidence(
            status=GeminiKeyStatus.VALID,
            detail="fixture valid",
        )


def test_real_gemini_keys_view_never_displays_raw_secret(tmp_path: Path, qtbot) -> None:
    raw_key = "raw-secret-" + "K" * 32
    service = GeminiKeyService(
        SqliteGeminiKeyRepository(tmp_path / "gemini.sqlite3"),
        MemorySecrets(),
        ValidHealth(),
    )
    service.import_text(f"Gemini Utama | {raw_key}")

    window = MainWindow(gemini_key_service=service)
    qtbot.addWidget(window)
    window.show_gemini_keys()

    assert window.fixture_code == "REAL_GEMINI_KEYS"
    tables = [table for table in window.findChildren(QTableWidget) if table.columnCount() == 5]
    assert tables
    table = tables[0]
    assert table.rowCount() == 1
    visible = " ".join(
        table.item(row, column).text()
        for row in range(table.rowCount())
        for column in range(table.columnCount())
        if table.item(row, column) is not None
    )
    assert "Gemini Utama" in visible
    assert "••••••••••" in visible
    assert raw_key not in visible

class PausedHealth:
    def __init__(self) -> None:
        self.entered = Event()
        self.release = Event()

    def check(self, api_key: str) -> GeminiKeyHealthEvidence:
        assert api_key
        self.entered.set()
        assert self.release.wait(5)
        return GeminiKeyHealthEvidence(status=GeminiKeyStatus.VALID, detail="checked")


def test_gemini_keys_qt_health_completion_keeps_manual_active_key(tmp_path: Path, qtbot) -> None:
    health = PausedHealth()
    repo = SqliteGeminiKeyRepository(tmp_path / "gemini.sqlite3")
    service = GeminiKeyService(repo, MemorySecrets(), health)
    service.import_text(f"First | {'A' * 40}\nSecond | {'B' * 40}")
    first = next(p for p in service.list_profiles() if p.label == "First")
    second = next(p for p in service.list_profiles() if p.label == "Second")
    window = MainWindow(gemini_key_service=service)
    qtbot.addWidget(window)
    window.show_gemini_keys()

    window._check_gemini_key(first.key_id)
    try:
        assert health.entered.wait(5)
        window._activate_gemini_key(second.key_id)
    finally:
        health.release.set()

    qtbot.waitUntil(
        lambda: repo.get(first.key_id) is not None
        and repo.get(first.key_id).status is GeminiKeyStatus.VALID,
        timeout=3000,
    )
    qtbot.waitUntil(
        lambda: next(p for p in service.list_profiles() if p.label == "Second").is_active,
        timeout=3000,
    )
    active = [p.label for p in service.list_profiles() if p.is_active]
    assert active == ["Second"]
    assert window.findChild(QTableWidget) is not None

