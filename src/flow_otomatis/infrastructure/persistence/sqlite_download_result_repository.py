"""SQLite adapter for local Download outcomes."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from flow_otomatis.domain.errors import StorageError
from flow_otomatis.domain.result import DownloadRecord, DownloadState


class SqliteDownloadResultRepository:
    """Persist Download independently from Generate in the project database."""

    def __init__(self, projects_root: Path) -> None:
        self._projects_root = projects_root

    def save(self, record: DownloadRecord) -> None:
        try:
            with self._connect(record.episode_id) as connection:
                self._create_schema(connection)
                connection.execute(
                    """
                    INSERT INTO download_results (
                        episode_id, scene_id, state, updated_at,
                        output_path, take, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (episode_id, scene_id) DO UPDATE SET
                        state = excluded.state,
                        updated_at = excluded.updated_at,
                        output_path = excluded.output_path,
                        take = excluded.take,
                        error_message = excluded.error_message
                    """,
                    (
                        record.episode_id,
                        record.scene_id,
                        record.state,
                        record.updated_at.isoformat(),
                        record.output_path,
                        record.take,
                        record.error_message,
                    ),
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Could not save download result: {exc}") from exc

    def save_failure_if_unconfirmed(self, record: DownloadRecord) -> None:
        """Store a failure only when no prior successful history exists.

        The conditional upsert is atomic across competing SQLite connections.
        """

        if record.state != DownloadState.FAILED:
            raise ValueError("Only FAILED records may use conditional failure persistence")
        try:
            with self._connect(record.episode_id) as connection:
                self._create_schema(connection)
                connection.execute(
                    """
                    INSERT INTO download_results (
                        episode_id, scene_id, state, updated_at,
                        output_path, take, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (episode_id, scene_id) DO UPDATE SET
                        state = excluded.state,
                        updated_at = excluded.updated_at,
                        output_path = excluded.output_path,
                        take = excluded.take,
                        error_message = excluded.error_message
                    WHERE download_results.state <> ?
                    """,
                    (
                        record.episode_id,
                        record.scene_id,
                        record.state,
                        record.updated_at.isoformat(),
                        record.output_path,
                        record.take,
                        record.error_message,
                        DownloadState.DOWNLOADED,
                    ),
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Could not save download failure: {exc}") from exc

    def get(self, episode_id: str, scene_id: str) -> DownloadRecord | None:
        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            return None
        try:
            with sqlite3.connect(db_path) as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                row = connection.execute(
                    """
                    SELECT * FROM download_results
                    WHERE episode_id = ? AND scene_id = ?
                    """,
                    (episode_id, scene_id),
                ).fetchone()
                return self._row_to_record(row) if row is not None else None
        except sqlite3.Error as exc:
            raise StorageError(f"Could not read download result: {exc}") from exc

    def list_for_episode(self, episode_id: str) -> tuple[DownloadRecord, ...]:
        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            return ()
        try:
            with sqlite3.connect(db_path) as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                rows = connection.execute(
                    """
                    SELECT * FROM download_results
                    WHERE episode_id = ?
                    ORDER BY scene_id
                    """,
                    (episode_id,),
                ).fetchall()
                return tuple(self._row_to_record(row) for row in rows)
        except sqlite3.Error as exc:
            raise StorageError(f"Could not list download results: {exc}") from exc

    def _connect(self, episode_id: str) -> sqlite3.Connection:
        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            raise StorageError(f"Project database not found: {episode_id}")
        return sqlite3.connect(db_path)

    def _db_path(self, episode_id: str) -> Path:
        return self._projects_root / episode_id / "project.sqlite3"

    def _create_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS download_results (
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

    def _row_to_record(self, row: sqlite3.Row) -> DownloadRecord:
        from datetime import datetime

        return DownloadRecord(
            episode_id=str(row["episode_id"]),
            scene_id=str(row["scene_id"]),
            state=str(row["state"]),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
            output_path=(str(row["output_path"]) if row["output_path"] is not None else None),
            take=int(row["take"]),
            error_message=(str(row["error_message"]) if row["error_message"] is not None else None),
        )
