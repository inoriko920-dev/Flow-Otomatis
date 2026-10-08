"""Read-only SQLite Download history regression for legacy project databases."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from flow_otomatis.domain.errors import StorageError
from flow_otomatis.domain.result import DownloadRecord, DownloadState
from flow_otomatis.infrastructure.persistence import SqliteDownloadResultRepository


def _database(projects_root: Path, *, episode_id: str = "EP_LEGACY") -> Path:
    path = projects_root / episode_id / "project.sqlite3"
    path.parent.mkdir(parents=True)
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE legacy_project_marker (id INTEGER PRIMARY KEY)")
        connection.execute("INSERT INTO legacy_project_marker (id) VALUES (1)")
        connection.commit()
    return path


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_history_table_absent(path: Path) -> None:
    with sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True) as connection:
        names = connection.execute(
            "SELECT name FROM sqlite_master WHERE name = 'download_results'"
        ).fetchall()
    assert names == []


def test_get_and_list_do_not_create_legacy_download_table(
    tmp_path: Path,
) -> None:
    projects_root = tmp_path / "projects"
    database = _database(projects_root)
    original_checksum = _digest(database)
    original_size = database.stat().st_size
    repository = SqliteDownloadResultRepository(projects_root)

    for _ in range(3):
        assert repository.get("EP_LEGACY", "SCENE_001") is None
        assert repository.list_for_episode("EP_LEGACY") == ()

    assert _digest(database) == original_checksum
    assert database.stat().st_size == original_size
    _assert_history_table_absent(database)
    assert not (database.parent / "project.sqlite3-journal").exists()


def test_get_and_list_do_not_create_missing_project_file(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    repository = SqliteDownloadResultRepository(projects_root)
    assert repository.get("EP_MISSING", "SCENE_001") is None
    assert repository.list_for_episode("EP_MISSING") == ()
    assert not projects_root.exists()


def test_reading_real_download_history_does_not_mutate_sqlite(
    tmp_path: Path,
) -> None:
    projects_root = tmp_path / "projects"
    database = _database(projects_root)
    repository = SqliteDownloadResultRepository(projects_root)
    now = datetime(2026, 10, 8, 5, 0, tzinfo=UTC)
    record = DownloadRecord(
        episode_id="EP_LEGACY",
        scene_id="SCENE_001",
        state=DownloadState.DOWNLOADED,
        updated_at=now,
        output_path=str((tmp_path / "SCENE_001.mp4").resolve()),
        take=1,
    )
    repository.save(record)
    committed_checksum = _digest(database)

    for _ in range(3):
        assert repository.get("EP_LEGACY", "SCENE_001") == record
        assert repository.get("EP_LEGACY", "SCENE_MISSING") is None
        assert repository.list_for_episode("EP_LEGACY") == (record,)

    assert _digest(database) == committed_checksum
    assert not (database.parent / "project.sqlite3-journal").exists()


def test_invalid_sqlite_is_reported_without_overwriting_source(
    tmp_path: Path,
) -> None:
    projects_root = tmp_path / "projects"
    path = projects_root / "EP_DAMAGED" / "project.sqlite3"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"deliberately invalid sqlite bytes")
    checksum = _digest(path)
    repository = SqliteDownloadResultRepository(projects_root)

    with pytest.raises(StorageError):
        repository.get("EP_DAMAGED", "SCENE_001")
    with pytest.raises(StorageError):
        repository.list_for_episode("EP_DAMAGED")

    assert _digest(path) == checksum


@pytest.mark.parametrize("column", ["updated_at", "take"])
def test_malformed_download_row_is_typed_and_source_is_unchanged(
    tmp_path: Path,
    column: str,
) -> None:
    projects_root = tmp_path / "projects"
    database = _database(projects_root)
    repository = SqliteDownloadResultRepository(projects_root)
    repository.save(
        DownloadRecord(
            episode_id="EP_LEGACY",
            scene_id="SCENE_001",
            state=DownloadState.FAILED,
            updated_at=datetime.now(UTC),
        )
    )
    with sqlite3.connect(database) as connection:
        connection.execute(f"UPDATE download_results SET {column} = ?", ("invalid",))
    before = _digest(database)
    with pytest.raises(StorageError):
        repository.get("EP_LEGACY", "SCENE_001")
    with pytest.raises(StorageError):
        repository.list_for_episode("EP_LEGACY")
    assert _digest(database) == before
