"""SQLite adapter for the durable serial generation queue."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from flow_otomatis.domain.errors import StorageError
from flow_otomatis.domain.job import GenerationJob, GenerationJobState


class SqliteGenerationJobRepository:
    """Store generation jobs in the same per-project SQLite database."""

    def __init__(self, projects_root: Path) -> None:
        self._projects_root = projects_root

    def ensure_jobs(self, jobs: Iterable[GenerationJob]) -> None:
        grouped: dict[str, list[GenerationJob]] = {}
        for job in jobs:
            grouped.setdefault(job.episode_id, []).append(job)

        for episode_id, episode_jobs in grouped.items():
            try:
                with self._connect(episode_id) as connection:
                    self._create_schema(connection)
                    connection.executemany(
                        """
                        INSERT OR IGNORE INTO generation_jobs (
                            job_id, episode_id, scene_id, target_duration_s,
                            flow_duration_s, state, created_at, updated_at,
                            remote_result_id, error_message
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            (
                                job.job_id,
                                job.episode_id,
                                job.scene_id,
                                job.target_duration_s,
                                job.flow_duration_s,
                                job.state.value,
                                job.created_at.isoformat(),
                                job.updated_at.isoformat(),
                                job.remote_result_id,
                                job.error_message,
                            )
                            for job in episode_jobs
                        ],
                    )
                    connection.commit()
            except sqlite3.Error as exc:
                raise StorageError(f"Could not ensure generation jobs: {exc}") from exc

    def claim_next(self, episode_id: str) -> GenerationJob | None:
        """Enforce R1 by refusing to claim while one RUNNING row exists."""

        try:
            with self._connect(episode_id) as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                running = connection.execute(
                    """
                    SELECT job_id FROM generation_jobs
                    WHERE episode_id = ? AND state = ?
                    LIMIT 1
                    """,
                    (episode_id, GenerationJobState.RUNNING.value),
                ).fetchone()
                if running is not None:
                    connection.commit()
                    return None

                row = connection.execute(
                    """
                    SELECT * FROM generation_jobs
                    WHERE episode_id = ? AND state = ?
                    ORDER BY created_at, scene_id
                    LIMIT 1
                    """,
                    (episode_id, GenerationJobState.QUEUED.value),
                ).fetchone()
                if row is None:
                    connection.commit()
                    return None

                now = datetime.now(UTC).isoformat()
                connection.execute(
                    """
                    UPDATE generation_jobs
                    SET state = ?, updated_at = ?, error_message = NULL
                    WHERE job_id = ?
                    """,
                    (GenerationJobState.RUNNING.value, now, str(row["job_id"])),
                )
                connection.commit()
                return self._load_job(connection, str(row["job_id"]))
        except sqlite3.Error as exc:
            raise StorageError(f"Could not claim generation job: {exc}") from exc

    def mark_generated(self, job_id: str, remote_result_id: str) -> GenerationJob:
        return self._finish(
            job_id,
            state=GenerationJobState.GENERATED,
            remote_result_id=remote_result_id,
            error_message=None,
        )

    def mark_failed(self, job_id: str, error_message: str) -> GenerationJob:
        return self._finish(
            job_id,
            state=GenerationJobState.FAILED,
            remote_result_id=None,
            error_message=error_message,
        )

    def list_for_episode(self, episode_id: str) -> tuple[GenerationJob, ...]:
        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            return ()
        try:
            with sqlite3.connect(db_path) as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                rows = connection.execute(
                    """
                    SELECT * FROM generation_jobs
                    WHERE episode_id = ?
                    ORDER BY created_at, scene_id
                    """,
                    (episode_id,),
                ).fetchall()
                return tuple(self._row_to_job(row) for row in rows)
        except sqlite3.Error as exc:
            raise StorageError(f"Could not list generation jobs: {exc}") from exc

    def _finish(
        self,
        job_id: str,
        *,
        state: GenerationJobState,
        remote_result_id: str | None,
        error_message: str | None,
    ) -> GenerationJob:
        episode_id = job_id.split(":", 1)[0]
        try:
            with self._connect(episode_id) as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                connection.execute(
                    """
                    UPDATE generation_jobs
                    SET state = ?, updated_at = ?, remote_result_id = ?, error_message = ?
                    WHERE job_id = ?
                    """,
                    (
                        state.value,
                        datetime.now(UTC).isoformat(),
                        remote_result_id,
                        error_message,
                        job_id,
                    ),
                )
                connection.commit()
                job = self._load_job(connection, job_id)
                if job is None:
                    raise StorageError(f"Generation job not found: {job_id}")
                return job
        except sqlite3.Error as exc:
            raise StorageError(f"Could not update generation job: {exc}") from exc

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
            CREATE TABLE IF NOT EXISTS generation_jobs (
                job_id TEXT PRIMARY KEY,
                episode_id TEXT NOT NULL,
                scene_id TEXT NOT NULL,
                target_duration_s REAL NOT NULL,
                flow_duration_s INTEGER NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                remote_result_id TEXT,
                error_message TEXT,
                UNIQUE (episode_id, scene_id)
            )
            """
        )

    def _load_job(
        self,
        connection: sqlite3.Connection,
        job_id: str,
    ) -> GenerationJob | None:
        row = connection.execute(
            "SELECT * FROM generation_jobs WHERE job_id = ?",
            (job_id,),
        ).fetchone()
        return self._row_to_job(row) if row is not None else None

    def _row_to_job(self, row: sqlite3.Row) -> GenerationJob:
        return GenerationJob(
            job_id=str(row["job_id"]),
            episode_id=str(row["episode_id"]),
            scene_id=str(row["scene_id"]),
            target_duration_s=float(row["target_duration_s"]),
            flow_duration_s=int(row["flow_duration_s"]),
            state=GenerationJobState(str(row["state"])),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
            remote_result_id=(
                str(row["remote_result_id"]) if row["remote_result_id"] is not None else None
            ),
            error_message=(
                str(row["error_message"]) if row["error_message"] is not None else None
            ),
        )
