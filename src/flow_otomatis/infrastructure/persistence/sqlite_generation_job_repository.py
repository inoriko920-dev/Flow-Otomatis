"""SQLite adapter for durable generation revisions, ownership leases, and recovery."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from flow_otomatis.domain.errors import StorageError
from flow_otomatis.domain.job import (
    GenerationAttentionCode,
    GenerationJob,
    GenerationJobState,
)

_SCHEMA_VERSION = 2
_SAFE_REPREPARE_ATTENTION = {
    GenerationAttentionCode.REQUEST_STALE,
    GenerationAttentionCode.AUTH_REQUIRED,
    GenerationAttentionCode.ORPHAN_PRE_SUBMIT,
    GenerationAttentionCode.LEGACY_UNVERIFIED,
}


class SqliteGenerationJobRepository:
    """Store generation jobs in the same per-project SQLite database."""

    def __init__(self, projects_root: Path) -> None:
        self._projects_root = projects_root

    def ensure_jobs(self, jobs: Iterable[GenerationJob]) -> None:
        """Compatibility alias for explicit request preparation."""

        self.prepare_jobs(jobs)

    def prepare_jobs(self, jobs: Iterable[GenerationJob]) -> None:
        grouped: dict[str, list[GenerationJob]] = {}
        for job in jobs:
            grouped.setdefault(job.episode_id, []).append(job)

        for episode_id, episode_jobs in grouped.items():
            try:
                with self._connect(episode_id) as connection:
                    connection.row_factory = sqlite3.Row
                    self._ensure_schema(connection)
                    connection.execute("BEGIN IMMEDIATE")
                    for job in episode_jobs:
                        self._prepare_one(connection, job)
                    connection.commit()
            except sqlite3.Error as exc:
                raise StorageError(f"Could not prepare generation jobs: {exc}") from exc

    def claim_next(
        self,
        episode_id: str,
        owner_id: str,
        *,
        lease_seconds: int,
        now: datetime | None = None,
    ) -> GenerationJob | None:
        """Claim one verified QUEUED row while respecting active ownership."""

        claim_time = now or datetime.now(UTC)
        try:
            with self._connect(episode_id) as connection:
                connection.row_factory = sqlite3.Row
                self._ensure_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                self._recover_expired_running(connection, episode_id, claim_time)

                blocking = connection.execute(
                    """
                    SELECT job_id FROM generation_jobs
                    WHERE episode_id = ? AND state IN (?, ?)
                    LIMIT 1
                    """,
                    (
                        episode_id,
                        GenerationJobState.RUNNING.value,
                        GenerationJobState.ATTENTION_REQUIRED.value,
                    ),
                ).fetchone()
                if blocking is not None:
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

                if row["request_fingerprint"] is None:
                    connection.execute(
                        """
                        UPDATE generation_jobs
                        SET state = ?, attention_code = ?, error_message = ?
                        WHERE job_id = ?
                        """,
                        (
                            GenerationJobState.ATTENTION_REQUIRED.value,
                            GenerationAttentionCode.LEGACY_UNVERIFIED.value,
                            "Queued request has no verifiable revision; prepare it again.",
                            str(row["job_id"]),
                        ),
                    )
                    connection.commit()
                    return None

                lease_expires = claim_time + timedelta(seconds=max(lease_seconds, 1))
                connection.execute(
                    """
                    UPDATE generation_jobs
                    SET state = ?, updated_at = ?, error_message = NULL,
                        attention_code = NULL, owner_id = ?, lease_expires_at = ?,
                        submit_started_at = NULL
                    WHERE job_id = ? AND state = ?
                    """,
                    (
                        GenerationJobState.RUNNING.value,
                        claim_time.isoformat(),
                        owner_id,
                        lease_expires.isoformat(),
                        str(row["job_id"]),
                        GenerationJobState.QUEUED.value,
                    ),
                )
                connection.commit()
                return self._load_job(connection, str(row["job_id"]))
        except sqlite3.Error as exc:
            raise StorageError(f"Could not claim generation job: {exc}") from exc

    def mark_submit_started(
        self,
        job_id: str,
        owner_id: str,
        *,
        lease_seconds: int,
        now: datetime | None = None,
    ) -> GenerationJob:
        submit_time = now or datetime.now(UTC)
        lease_expires = submit_time + timedelta(seconds=max(lease_seconds, 1))
        episode_id = job_id.split(":", 1)[0]
        try:
            with self._connect(episode_id) as connection:
                connection.row_factory = sqlite3.Row
                self._ensure_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                cursor = connection.execute(
                    """
                    UPDATE generation_jobs
                    SET submit_started_at = COALESCE(submit_started_at, ?),
                        lease_expires_at = ?, updated_at = ?
                    WHERE job_id = ? AND state = ? AND owner_id = ?
                    """,
                    (
                        submit_time.isoformat(),
                        lease_expires.isoformat(),
                        submit_time.isoformat(),
                        job_id,
                        GenerationJobState.RUNNING.value,
                        owner_id,
                    ),
                )
                if cursor.rowcount != 1:
                    connection.rollback()
                    raise StorageError(f"Generation job ownership was lost: {job_id}")
                connection.commit()
                job = self._load_job(connection, job_id)
                if job is None:
                    raise StorageError(f"Generation job not found: {job_id}")
                return job
        except sqlite3.Error as exc:
            raise StorageError(f"Could not mark generation submit boundary: {exc}") from exc

    def mark_generated(
        self,
        job_id: str,
        remote_result_id: str,
        owner_id: str,
    ) -> GenerationJob:
        return self._finish_owned(
            job_id,
            owner_id,
            state=GenerationJobState.GENERATED,
            remote_result_id=remote_result_id,
            error_message=None,
            attention_code=None,
        )

    def mark_attention(
        self,
        job_id: str,
        error_message: str,
        attention_code: GenerationAttentionCode,
        owner_id: str,
    ) -> GenerationJob:
        return self._finish_owned(
            job_id,
            owner_id,
            state=GenerationJobState.ATTENTION_REQUIRED,
            remote_result_id=None,
            error_message=error_message,
            attention_code=attention_code,
        )

    def mark_failed(
        self,
        job_id: str,
        error_message: str,
        owner_id: str,
    ) -> GenerationJob:
        return self._finish_owned(
            job_id,
            owner_id,
            state=GenerationJobState.FAILED,
            remote_result_id=None,
            error_message=error_message,
            attention_code=None,
        )

    def recover_expired(
        self,
        episode_id: str,
        *,
        now: datetime | None = None,
    ) -> tuple[GenerationJob, ...]:
        recovery_time = now or datetime.now(UTC)
        try:
            with self._connect(episode_id) as connection:
                connection.row_factory = sqlite3.Row
                self._ensure_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                recovered_ids = self._recover_expired_running(
                    connection,
                    episode_id,
                    recovery_time,
                )
                connection.commit()
                return tuple(
                    job
                    for job_id in recovered_ids
                    if (job := self._load_job(connection, job_id)) is not None
                )
        except sqlite3.Error as exc:
            raise StorageError(f"Could not recover expired generation jobs: {exc}") from exc

    def list_for_episode(self, episode_id: str) -> tuple[GenerationJob, ...]:
        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            return ()
        try:
            # Read-only URI prevents list/snapshot from creating tables, WAL
            # journals, or implicitly migrating a historical project.
            with sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True) as connection:
                connection.row_factory = sqlite3.Row
                connection.execute("BEGIN")
                self._check_supported_schema(connection)
                exists = connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'generation_jobs'"
                ).fetchone()
                if exists is None:
                    return ()
                rows = connection.execute(
                    """
                    SELECT * FROM generation_jobs
                    WHERE episode_id = ?
                    ORDER BY created_at, scene_id
                    """,
                    (episode_id,),
                ).fetchall()
                return tuple(self._row_to_job(row) for row in rows)
        except (sqlite3.Error, ValueError, TypeError, KeyError) as exc:
            raise StorageError("Generation history could not be read safely") from exc

    def _prepare_one(
        self,
        connection: sqlite3.Connection,
        job: GenerationJob,
    ) -> None:
        existing = connection.execute(
            "SELECT * FROM generation_jobs WHERE job_id = ?",
            (job.job_id,),
        ).fetchone()
        if existing is None:
            state = job.state
            attention_code = job.attention_code
            error_message = job.error_message
            if job.request_fingerprint is None and state is GenerationJobState.QUEUED:
                state = GenerationJobState.ATTENTION_REQUIRED
                attention_code = GenerationAttentionCode.LEGACY_UNVERIFIED
                error_message = "Queued request has no verifiable revision; prepare it again."
            connection.execute(
                """
                INSERT INTO generation_jobs (
                    job_id, episode_id, scene_id, target_duration_s,
                    flow_duration_s, state, created_at, updated_at,
                    image_file, motion_prompt, model, resolution, aspect_ratio,
                    request_fingerprint, remote_result_id, error_message,
                    attention_code, owner_id, lease_expires_at, submit_started_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._job_values(
                    job,
                    state=state,
                    attention_code=attention_code,
                    error_message=error_message,
                ),
            )
            return

        existing_state = GenerationJobState(str(existing["state"]))
        if existing_state in {GenerationJobState.GENERATED, GenerationJobState.RUNNING}:
            return

        if existing_state is GenerationJobState.ATTENTION_REQUIRED:
            raw_code = existing["attention_code"]
            existing_code = GenerationAttentionCode(str(raw_code)) if raw_code is not None else None
            if existing_code not in _SAFE_REPREPARE_ATTENTION:
                return

        connection.execute(
            """
            UPDATE generation_jobs
            SET target_duration_s = ?, flow_duration_s = ?, state = ?,
                updated_at = ?, image_file = ?, motion_prompt = ?,
                model = ?, resolution = ?, aspect_ratio = ?,
                request_fingerprint = ?, remote_result_id = NULL,
                error_message = NULL, attention_code = NULL,
                owner_id = NULL, lease_expires_at = NULL,
                submit_started_at = NULL
            WHERE job_id = ?
            """,
            (
                job.target_duration_s,
                job.flow_duration_s,
                GenerationJobState.QUEUED.value,
                job.updated_at.isoformat(),
                job.image_file,
                job.motion_prompt,
                job.model,
                job.resolution,
                job.aspect_ratio,
                job.request_fingerprint,
                job.job_id,
            ),
        )

    def _job_values(
        self,
        job: GenerationJob,
        *,
        state: GenerationJobState,
        attention_code: GenerationAttentionCode | None,
        error_message: str | None,
    ) -> tuple[object, ...]:
        return (
            job.job_id,
            job.episode_id,
            job.scene_id,
            job.target_duration_s,
            job.flow_duration_s,
            state.value,
            job.created_at.isoformat(),
            job.updated_at.isoformat(),
            job.image_file,
            job.motion_prompt,
            job.model,
            job.resolution,
            job.aspect_ratio,
            job.request_fingerprint,
            job.remote_result_id,
            error_message,
            attention_code.value if attention_code is not None else None,
            job.owner_id,
            job.lease_expires_at.isoformat() if job.lease_expires_at is not None else None,
            job.submit_started_at.isoformat() if job.submit_started_at is not None else None,
        )

    def _finish_owned(
        self,
        job_id: str,
        owner_id: str,
        *,
        state: GenerationJobState,
        remote_result_id: str | None,
        error_message: str | None,
        attention_code: GenerationAttentionCode | None,
    ) -> GenerationJob:
        episode_id = job_id.split(":", 1)[0]
        try:
            with self._connect(episode_id) as connection:
                connection.row_factory = sqlite3.Row
                self._ensure_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                cursor = connection.execute(
                    """
                    UPDATE generation_jobs
                    SET state = ?, updated_at = ?, remote_result_id = ?,
                        error_message = ?, attention_code = ?
                    WHERE job_id = ? AND state = ? AND owner_id = ?
                    """,
                    (
                        state.value,
                        datetime.now(UTC).isoformat(),
                        remote_result_id,
                        error_message,
                        attention_code.value if attention_code is not None else None,
                        job_id,
                        GenerationJobState.RUNNING.value,
                        owner_id,
                    ),
                )
                if cursor.rowcount != 1:
                    connection.rollback()
                    raise StorageError(f"Generation job ownership was lost: {job_id}")
                connection.commit()
                job = self._load_job(connection, job_id)
                if job is None:
                    raise StorageError(f"Generation job not found: {job_id}")
                return job
        except sqlite3.Error as exc:
            raise StorageError(f"Could not update generation job: {exc}") from exc

    def _recover_expired_running(
        self,
        connection: sqlite3.Connection,
        episode_id: str,
        now: datetime,
    ) -> list[str]:
        rows = connection.execute(
            """
            SELECT job_id, submit_started_at FROM generation_jobs
            WHERE episode_id = ? AND state = ?
              AND lease_expires_at IS NOT NULL
              AND lease_expires_at <= ?
            ORDER BY created_at, scene_id
            """,
            (
                episode_id,
                GenerationJobState.RUNNING.value,
                now.isoformat(),
            ),
        ).fetchall()
        recovered_ids: list[str] = []
        for row in rows:
            job_id = str(row["job_id"])
            submit_started = row["submit_started_at"] is not None
            code = (
                GenerationAttentionCode.ORPHAN_POSSIBLE_SUBMIT
                if submit_started
                else GenerationAttentionCode.ORPHAN_PRE_SUBMIT
            )
            message = (
                "Worker lease expired after the submit boundary; provider outcome may be "
                "ambiguous. Automatic resubmit is forbidden."
                if submit_started
                else (
                    "Worker lease expired before the submit boundary; the job is parked for "
                    "explicit re-prepare and will not auto-submit."
                )
            )
            connection.execute(
                """
                UPDATE generation_jobs
                SET state = ?, attention_code = ?, error_message = ?, updated_at = ?
                WHERE job_id = ? AND state = ?
                """,
                (
                    GenerationJobState.ATTENTION_REQUIRED.value,
                    code.value,
                    message,
                    now.isoformat(),
                    job_id,
                    GenerationJobState.RUNNING.value,
                ),
            )
            recovered_ids.append(job_id)
        return recovered_ids

    def _connect(self, episode_id: str) -> sqlite3.Connection:
        db_path = self._db_path(episode_id)
        if not db_path.is_file():
            raise StorageError(f"Project database not found: {episode_id}")
        return sqlite3.connect(db_path)

    def _db_path(self, episode_id: str) -> Path:
        return self._projects_root / episode_id / "project.sqlite3"

    def _check_supported_schema(self, connection: sqlite3.Connection) -> None:
        """Reject future schema markers on both read and write, without repair."""

        marker = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'generation_job_schema'"
        ).fetchone()
        if marker is None:
            return
        row = connection.execute(
            "SELECT schema_version FROM generation_job_schema WHERE singleton = 1"
        ).fetchone()
        if row is None:
            raise StorageError("Generation history schema marker is incomplete")
        try:
            version = int(row[0])
        except (TypeError, ValueError) as exc:
            raise StorageError("Generation history schema marker is invalid") from exc
        if version > _SCHEMA_VERSION or version < 1:
            raise StorageError("Unsupported generation history schema version")

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        """Create or transactionally migrate the queue schema to version 2."""

        try:
            connection.execute("BEGIN IMMEDIATE")
            self._check_supported_schema(connection)
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS generation_job_schema (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    schema_version INTEGER NOT NULL
                )
                """
            )
            exists = connection.execute(
                """
                SELECT 1 FROM sqlite_master
                WHERE type = 'table' AND name = 'generation_jobs'
                """
            ).fetchone()
            if exists is None:
                self._create_latest_table(connection)
            else:
                columns = {
                    str(row[1])
                    for row in connection.execute("PRAGMA table_info(generation_jobs)").fetchall()
                }
                additions = (
                    ("image_file", "TEXT"),
                    ("motion_prompt", "TEXT"),
                    ("model", "TEXT"),
                    ("resolution", "TEXT"),
                    ("aspect_ratio", "TEXT"),
                    ("request_fingerprint", "TEXT"),
                    ("attention_code", "TEXT"),
                    ("owner_id", "TEXT"),
                    ("lease_expires_at", "TEXT"),
                    ("submit_started_at", "TEXT"),
                )
                for name, sql_type in additions:
                    if name not in columns:
                        connection.execute(
                            f"ALTER TABLE generation_jobs ADD COLUMN {name} {sql_type}"
                        )

                connection.execute(
                    """
                    UPDATE generation_jobs
                    SET state = ?, attention_code = COALESCE(attention_code, ?),
                        error_message = COALESCE(
                            error_message,
                            'Legacy queued request has no verifiable revision; prepare it again.'
                        )
                    WHERE request_fingerprint IS NULL AND state = ?
                    """,
                    (
                        GenerationJobState.ATTENTION_REQUIRED.value,
                        GenerationAttentionCode.LEGACY_UNVERIFIED.value,
                        GenerationJobState.QUEUED.value,
                    ),
                )
                connection.execute(
                    """
                    UPDATE generation_jobs
                    SET state = ?, attention_code = COALESCE(attention_code, ?),
                        error_message = COALESCE(
                            error_message,
                            'Legacy RUNNING request has no trustworthy lease/revision; '
                            || 'automatic resubmit is forbidden.'
                        )
                    WHERE request_fingerprint IS NULL AND state = ?
                    """,
                    (
                        GenerationJobState.ATTENTION_REQUIRED.value,
                        GenerationAttentionCode.LEGACY_RUNNING_UNVERIFIED.value,
                        GenerationJobState.RUNNING.value,
                    ),
                )

            connection.execute(
                """
                INSERT INTO generation_job_schema (singleton, schema_version)
                VALUES (1, ?)
                ON CONFLICT(singleton) DO UPDATE SET schema_version = excluded.schema_version
                """,
                (_SCHEMA_VERSION,),
            )
            connection.commit()
        except sqlite3.Error:
            connection.rollback()
            raise

    def _create_latest_table(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE generation_jobs (
                job_id TEXT PRIMARY KEY,
                episode_id TEXT NOT NULL,
                scene_id TEXT NOT NULL,
                target_duration_s REAL NOT NULL,
                flow_duration_s INTEGER NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                image_file TEXT,
                motion_prompt TEXT,
                model TEXT,
                resolution TEXT,
                aspect_ratio TEXT,
                request_fingerprint TEXT,
                remote_result_id TEXT,
                error_message TEXT,
                attention_code TEXT,
                owner_id TEXT,
                lease_expires_at TEXT,
                submit_started_at TEXT,
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
        # Pre-v2 records can be decoded without mutating their schema.
        def optional(column: str) -> object | None:
            try:
                return row[column]
            except (IndexError, KeyError):
                return None

        attention_raw = optional("attention_code")
        return GenerationJob(
            job_id=str(row["job_id"]),
            episode_id=str(row["episode_id"]),
            scene_id=str(row["scene_id"]),
            target_duration_s=float(row["target_duration_s"]),
            flow_duration_s=int(row["flow_duration_s"]),
            state=GenerationJobState(str(row["state"])),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
            image_file=str(optional("image_file")) if optional("image_file") is not None else None,
            motion_prompt=(
                str(optional("motion_prompt")) if optional("motion_prompt") is not None else None
            ),
            model=str(optional("model")) if optional("model") is not None else None,
            resolution=str(optional("resolution")) if optional("resolution") is not None else None,
            aspect_ratio=(
                str(optional("aspect_ratio")) if optional("aspect_ratio") is not None else None
            ),
            request_fingerprint=(
                str(optional("request_fingerprint"))
                if optional("request_fingerprint") is not None
                else None
            ),
            remote_result_id=(
                str(optional("remote_result_id"))
                if optional("remote_result_id") is not None
                else None
            ),
            error_message=(
                str(optional("error_message")) if optional("error_message") is not None else None
            ),
            attention_code=(
                GenerationAttentionCode(str(attention_raw)) if attention_raw is not None else None
            ),
            owner_id=str(optional("owner_id")) if optional("owner_id") is not None else None,
            lease_expires_at=(
                datetime.fromisoformat(str(optional("lease_expires_at")))
                if optional("lease_expires_at") is not None
                else None
            ),
            submit_started_at=(
                datetime.fromisoformat(str(optional("submit_started_at")))
                if optional("submit_started_at") is not None
                else None
            ),
        )
