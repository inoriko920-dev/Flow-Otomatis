"""SQLite adapter for local Download outcomes."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from flow_otomatis.domain.errors import StorageError, WorkspaceCorruptError
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
                        output_path, take, error_message,
                        generation_remote_result_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (episode_id, scene_id) DO UPDATE SET
                        state = excluded.state,
                        updated_at = excluded.updated_at,
                        output_path = excluded.output_path,
                        take = excluded.take,
                        error_message = excluded.error_message,
                        generation_remote_result_id = excluded.generation_remote_result_id
                    """,
                    (
                        record.episode_id,
                        record.scene_id,
                        record.state,
                        record.updated_at.isoformat(),
                        record.output_path,
                        record.take,
                        record.error_message,
                        record.generation_remote_result_id,
                    ),
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Could not save download result: {exc}") from exc

    def save_if_current_generate(
        self, record: DownloadRecord, expected_remote_result_id: str
    ) -> bool:
        """Compare current Generate and persist Download in one SQLite write lock.

        The BEGIN IMMEDIATE transaction serializes this check against a
        concurrent Generate state/ID change from another process. A stale
        result is rejected without writing any Download row or touching MP4.
        """

        if record.state != DownloadState.DOWNLOADED:
            raise ValueError("Only DOWNLOADED records can use guarded success persistence")
        remote_id = expected_remote_result_id.strip()
        if not remote_id:
            raise ValueError("Expected Generate remote ID must not be blank")
        # A caller must not ask this adapter to certify bytes as belonging to
        # a different Generate result. Validate before opening the database.
        if record.generation_remote_result_id != remote_id:
            raise ValueError("Download record Generate identity does not match expected ID")
        try:
            with self._connect(record.episode_id) as connection:
                self._create_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                current = connection.execute(
                    """
                    SELECT 1 FROM generation_jobs
                    WHERE episode_id = ? AND scene_id = ?
                      AND state = 'GENERATED'
                      AND TRIM(COALESCE(remote_result_id, '')) = ?
                    LIMIT 1
                    """,
                    (record.episode_id, record.scene_id, remote_id),
                ).fetchone()
                if current is None:
                    connection.rollback()
                    return False
                cursor = connection.execute(
                    """
                    INSERT INTO download_results (
                        episode_id, scene_id, state, updated_at,
                        output_path, take, error_message,
                        generation_remote_result_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (episode_id, scene_id) DO UPDATE SET
                        state = excluded.state,
                        updated_at = excluded.updated_at,
                        output_path = excluded.output_path,
                        take = excluded.take,
                        error_message = excluded.error_message,
                        generation_remote_result_id = excluded.generation_remote_result_id
                    WHERE download_results.state <> 'DOWNLOADED'
                       OR download_results.generation_remote_result_id =
                          excluded.generation_remote_result_id
                    """,
                    (
                        record.episode_id,
                        record.scene_id,
                        record.state,
                        record.updated_at.isoformat(),
                        record.output_path,
                        record.take,
                        record.error_message,
                        remote_id,
                    ),
                )
                if cursor.rowcount != 1:
                    # Never replace the only surviving evidence of a different
                    # Generate result, including legacy records with no remote ID.
                    # Its MP4 and stored history require explicit reconciliation.
                    connection.rollback()
                    return False
                connection.commit()
                return True
        except sqlite3.Error as exc:
            raise StorageError("Could not atomically verify and save Download result") from exc

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
                        output_path, take, error_message,
                        generation_remote_result_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (episode_id, scene_id) DO UPDATE SET
                        state = excluded.state,
                        updated_at = excluded.updated_at,
                        output_path = excluded.output_path,
                        take = excluded.take,
                        error_message = excluded.error_message,
                        generation_remote_result_id = excluded.generation_remote_result_id
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
                        record.generation_remote_result_id,
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
            with self._connect_readonly(db_path) as connection:
                connection.row_factory = sqlite3.Row
                if not self._has_download_results_table(connection):
                    return None
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
        except (ValueError, TypeError, IndexError, OverflowError) as exc:
            raise WorkspaceCorruptError(episode_id) from exc

    def list_for_episode(self, episode_id: str) -> tuple[DownloadRecord, ...]:
        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            return ()
        try:
            with self._connect_readonly(db_path) as connection:
                connection.row_factory = sqlite3.Row
                if not self._has_download_results_table(connection):
                    return ()
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
        except (ValueError, TypeError, IndexError, OverflowError) as exc:
            raise WorkspaceCorruptError(episode_id) from exc

    def _connect(self, episode_id: str) -> sqlite3.Connection:
        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            raise StorageError(f"Project database not found: {episode_id}")
        return sqlite3.connect(db_path)

    @staticmethod
    def _connect_readonly(db_path: Path) -> sqlite3.Connection:
        """Never initialize or change SQLite when a user only views results."""

        uri = f"{db_path.resolve().as_uri()}?mode=ro"
        return sqlite3.connect(uri, uri=True)

    @staticmethod
    def _has_download_results_table(connection: sqlite3.Connection) -> bool:
        """Old projects may not yet have Download history; leave them unchanged."""

        return (
            connection.execute(
                """
                SELECT 1 FROM sqlite_master
                WHERE type = 'table' AND name = 'download_results'
                LIMIT 1
                """
            ).fetchone()
            is not None
        )

    def _db_path(self, episode_id: str) -> Path:
        # DB reads and failure writes can be called without the browser
        # Download service. Reject traversal/Windows aliases at this boundary,
        # before any filesystem access, including SQLite mode=ro reads.
        forbidden = '<>:"/\\|?*'
        reserved = (
            {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
            | {f"COM{i}" for i in range(1, 10)}
            | {f"LPT{i}" for i in range(1, 10)}
        )
        if (
            not isinstance(episode_id, str)
            or not episode_id
            or episode_id in {".", ".."}
            or episode_id.endswith((".", " "))
            or any(char in forbidden or ord(char) < 32 for char in episode_id)
            or episode_id.split(".", 1)[0].upper() in reserved
        ):
            raise StorageError("Unsafe project episode identifier")
        db_path = self._projects_root / episode_id / "project.sqlite3"
        try:
            # A harmless-looking episode ID may refer to a redirected project
            # directory (Windows junction, symlink) or a linked database file.
            # Never read or write through such paths, even in read-only views.
            if any(
                node.is_symlink() or node.is_junction()
                for node in (self._projects_root, db_path.parent, db_path)
            ):
                raise StorageError("Project database path is redirected")
        except (OSError, RuntimeError, ValueError) as exc:
            raise StorageError("Project database path cannot be safely verified") from exc
        return db_path

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
                generation_remote_result_id TEXT,
                PRIMARY KEY (episode_id, scene_id)
            )
            """
        )
        # A legacy schema is only migrated on a real write, not on get/list.
        columns = {str(row[1]) for row in connection.execute("PRAGMA table_info(download_results)")}
        if "generation_remote_result_id" not in columns:
            connection.execute(
                "ALTER TABLE download_results ADD COLUMN generation_remote_result_id TEXT"
            )

    def _row_to_record(self, row: sqlite3.Row) -> DownloadRecord:
        from datetime import datetime

        # sqlite3.Row membership checks values, not column names.
        columns = row.keys()
        return DownloadRecord(
            episode_id=str(row["episode_id"]),
            scene_id=str(row["scene_id"]),
            state=str(row["state"]),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
            output_path=(str(row["output_path"]) if row["output_path"] is not None else None),
            take=int(row["take"]),
            error_message=(str(row["error_message"]) if row["error_message"] is not None else None),
            generation_remote_result_id=(
                str(row["generation_remote_result_id"])
                if "generation_remote_result_id" in columns
                and row["generation_remote_result_id"] is not None
                else None
            ),
        )
