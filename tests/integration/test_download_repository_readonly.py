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


def test_legacy_success_history_is_read_only_until_explicit_new_write(tmp_path: Path) -> None:
    """Old project databases get no fake remote ID and no read-time migrations."""

    projects_root = tmp_path / "projects"
    database = _database(projects_root)
    now = datetime(2026, 10, 10, 5, 0, tzinfo=UTC)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE download_results (
                episode_id TEXT NOT NULL,
                scene_id TEXT NOT NULL,
                state TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                output_path TEXT,
                take INTEGER NOT NULL,
                error_message TEXT,
                PRIMARY KEY (episode_id, scene_id)
            )
            """
        )
        connection.execute(
            """
            INSERT INTO download_results (
                episode_id, scene_id, state, updated_at, output_path, take, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("EP_LEGACY", "SCENE_001", "DOWNLOADED", now.isoformat(), "legacy.mp4", 1, None),
        )
        connection.commit()

    before = _digest(database)
    repository = SqliteDownloadResultRepository(projects_root)
    record = repository.get("EP_LEGACY", "SCENE_001")
    assert record is not None
    assert record.state == DownloadState.DOWNLOADED
    assert record.generation_remote_result_id is None
    assert repository.list_for_episode("EP_LEGACY") == (record,)
    assert _digest(database) == before
    with sqlite3.connect(database) as connection:
        names = {str(row[1]) for row in connection.execute("PRAGMA table_info(download_results)")}
    assert "generation_remote_result_id" not in names

    from dataclasses import replace

    repository.save(replace(record, generation_remote_result_id="remote:CONFIRMED"))
    upgraded = repository.get("EP_LEGACY", "SCENE_001")
    assert upgraded is not None
    assert upgraded.generation_remote_result_id == "remote:CONFIRMED"
    assert upgraded.output_path == "legacy.mp4"
    with sqlite3.connect(database) as connection:
        upgraded_names = {
            str(row[1]) for row in connection.execute("PRAGMA table_info(download_results)")
        }
    assert "generation_remote_result_id" in upgraded_names


@pytest.mark.parametrize(
    "unsafe_id",
    [
        "",
        ".",
        "..",
        "../EP_LEGACY",
        "EP_LEGACY/../../outside",
        r"..\\EP_LEGACY",
        r"C:\\outside",
        "EP_LEGACY:other",
        "EP_LEGACY.",
        "EP_LEGACY ",
        "EP_LEGACY\\nested",
        "CON",
        "PRN.txt",
        "NUL",
        "COM1",
        "LPT9",
        "EP_BAD\\x00",
    ],
)
def test_download_database_boundary_rejects_unsafe_episode_paths(
    tmp_path: Path, unsafe_id: str
) -> None:
    """Direct DB access must not bypass the service-level Windows path gate."""

    projects_root = tmp_path / "projects"
    untouched = _database(projects_root)
    before = _digest(untouched)
    repository = SqliteDownloadResultRepository(projects_root)
    failed = DownloadRecord(
        episode_id=unsafe_id,
        scene_id="SCENE_001",
        state=DownloadState.FAILED,
        updated_at=datetime.now(UTC),
        error_message="synthetic failure",
    )
    downloaded = DownloadRecord(
        episode_id=unsafe_id,
        scene_id="SCENE_001",
        state=DownloadState.DOWNLOADED,
        updated_at=datetime.now(UTC),
        output_path=str(tmp_path / "safe.mp4"),
        generation_remote_result_id="remote:GOOD",
    )

    with pytest.raises(StorageError, match="Unsafe project episode"):
        repository.get(unsafe_id, "SCENE_001")
    with pytest.raises(StorageError, match="Unsafe project episode"):
        repository.list_for_episode(unsafe_id)
    with pytest.raises(StorageError, match="Unsafe project episode"):
        repository.save(failed)
    with pytest.raises(StorageError, match="Unsafe project episode"):
        repository.save_failure_if_unconfirmed(failed)
    with pytest.raises(StorageError, match="Unsafe project episode"):
        repository.save_if_current_generate(downloaded, "remote:GOOD")

    assert _digest(untouched) == before
    assert sorted(p.name for p in projects_root.iterdir()) == ["EP_LEGACY"]


@pytest.mark.parametrize("bad_identity", [None, "", "remote:DIFFERENT", " remote:GOOD "])
def test_atomic_download_rejects_contradictory_generate_binding_before_database_io(
    tmp_path: Path, bad_identity: str | None
) -> None:
    """A guarded commit cannot relabel a Download from the wrong Generate ID."""

    projects_root = tmp_path / "projects"
    database = _database(projects_root)
    repository = SqliteDownloadResultRepository(projects_root)
    before = _digest(database)
    record = DownloadRecord(
        episode_id="EP_LEGACY",
        scene_id="SCENE_001",
        state=DownloadState.DOWNLOADED,
        updated_at=datetime.now(UTC),
        output_path=str(tmp_path / "video.mp4"),
        generation_remote_result_id=bad_identity,
    )

    with pytest.raises(ValueError, match="identity does not match"):
        repository.save_if_current_generate(record, "remote:GOOD")

    assert _digest(database) == before
    _assert_history_table_absent(database)


@pytest.mark.parametrize("redirect", ["project", "database"])
def test_download_database_boundary_blocks_real_symlink_escape(
    tmp_path: Path, redirect: str
) -> None:
    """A valid episode name cannot be redirected to an outside SQLite file."""

    external = _database(tmp_path / "external", episode_id="EP_OUTSIDE")
    before = _digest(external)
    projects_root = tmp_path / "projects"
    project = projects_root / "EP_LINK"
    project.parent.mkdir()
    if redirect == "project":
        link = project
        target = external.parent
        is_directory = True
    else:
        project.mkdir()
        link = project / "project.sqlite3"
        target = external
        is_directory = False
    try:
        link.symlink_to(target, target_is_directory=is_directory)
    except (OSError, NotImplementedError):
        pytest.skip("Runner cannot create symbolic links")

    repository = SqliteDownloadResultRepository(projects_root)
    record = DownloadRecord(
        episode_id="EP_LINK",
        scene_id="SCENE_001",
        state=DownloadState.FAILED,
        updated_at=datetime.now(UTC),
        error_message="synthetic",
    )
    with pytest.raises(StorageError, match="redirected"):
        repository.get("EP_LINK", "SCENE_001")
    with pytest.raises(StorageError, match="redirected"):
        repository.save_failure_if_unconfirmed(record)
    assert _digest(external) == before


def test_download_database_boundary_blocks_windows_junction_without_symlink_privilege(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Model a Windows NTFS junction independently of runner privileges."""

    projects_root = tmp_path / "projects"
    database = _database(projects_root)
    original = _digest(database)
    is_junction = Path.is_junction

    def redirect_project(self: Path) -> bool:
        return self == database.parent or is_junction(self)

    monkeypatch.setattr(Path, "is_junction", redirect_project)
    repository = SqliteDownloadResultRepository(projects_root)
    with pytest.raises(StorageError, match="redirected"):
        repository.list_for_episode("EP_LEGACY")
    with pytest.raises(StorageError, match="redirected"):
        repository.save(
            DownloadRecord(
                episode_id="EP_LEGACY",
                scene_id="SCENE_001",
                state=DownloadState.FAILED,
                updated_at=datetime.now(UTC),
            )
        )
    assert _digest(database) == original
