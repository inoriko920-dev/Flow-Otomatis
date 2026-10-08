"""SQLite metadata repository for Gemini keys. Raw secrets are never stored here."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from flow_otomatis.domain.errors import StorageError
from flow_otomatis.domain.gemini import GeminiKeyProfile, GeminiKeyStatus


class SqliteGeminiKeyRepository:
    """Persist only masked/fingerprinted Gemini key metadata."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def list_profiles(self) -> tuple[GeminiKeyProfile, ...]:
        if not self._db_path.is_file():
            return ()
        try:
            with self._connect() as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                rows = connection.execute(
                    """
                    SELECT * FROM gemini_keys
                    ORDER BY is_active DESC, label COLLATE NOCASE, key_id
                    """
                ).fetchall()
                return tuple(self._row(row) for row in rows)
        except sqlite3.Error as exc:
            raise StorageError(f"Could not list Gemini key metadata: {exc}") from exc

    def get(self, key_id: str) -> GeminiKeyProfile | None:
        if not self._db_path.is_file():
            return None
        try:
            with self._connect() as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                row = connection.execute(
                    "SELECT * FROM gemini_keys WHERE key_id = ?",
                    (key_id,),
                ).fetchone()
                return self._row(row) if row is not None else None
        except sqlite3.Error as exc:
            raise StorageError(f"Could not read Gemini key metadata: {exc}") from exc

    def find_by_fingerprint(self, fingerprint: str) -> GeminiKeyProfile | None:
        if not self._db_path.is_file():
            return None
        try:
            with self._connect() as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                row = connection.execute(
                    "SELECT * FROM gemini_keys WHERE fingerprint = ?",
                    (fingerprint,),
                ).fetchone()
                return self._row(row) if row is not None else None
        except sqlite3.Error as exc:
            raise StorageError(f"Could not search Gemini key metadata: {exc}") from exc

    def save(self, profile: GeminiKeyProfile) -> None:
        try:
            with self._connect() as connection:
                self._create_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                if profile.is_active:
                    connection.execute("UPDATE gemini_keys SET is_active = 0")
                connection.execute(
                    """
                    INSERT INTO gemini_keys (
                        key_id, label, masked_key, fingerprint, status,
                        last_checked_at, is_active, detail
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(key_id) DO UPDATE SET
                        label = excluded.label,
                        masked_key = excluded.masked_key,
                        fingerprint = excluded.fingerprint,
                        status = excluded.status,
                        last_checked_at = excluded.last_checked_at,
                        is_active = excluded.is_active,
                        detail = excluded.detail
                    """,
                    (
                        profile.key_id,
                        profile.label,
                        profile.masked_key,
                        profile.fingerprint,
                        profile.status.value,
                        (
                            profile.last_checked_at.isoformat()
                            if profile.last_checked_at is not None
                            else None
                        ),
                        int(profile.is_active),
                        profile.detail,
                    ),
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Could not save Gemini key metadata: {exc}") from exc

    def update_health(
        self,
        key_id: str,
        status: GeminiKeyStatus,
        checked_at: datetime,
        detail: str,
    ) -> GeminiKeyProfile | None:
        """Update health of a still-existing key without upsert or activation changes."""

        if not self._db_path.is_file():
            return None
        try:
            with self._connect() as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                updated = connection.execute(
                    """
                    UPDATE gemini_keys
                    SET status = ?, last_checked_at = ?, detail = ?
                    WHERE key_id = ?
                    """,
                    (status.value, checked_at.isoformat(), detail[:300], key_id),
                )
                if updated.rowcount != 1:
                    return None
                row = connection.execute(
                    "SELECT * FROM gemini_keys WHERE key_id = ?", (key_id,)
                ).fetchone()
                return self._row(row) if row is not None else None
        except sqlite3.Error as exc:
            raise StorageError(f"Could not update Gemini key health: {exc}") from exc

    def set_active(self, key_id: str) -> GeminiKeyProfile:
        try:
            with self._connect() as connection:
                connection.row_factory = sqlite3.Row
                self._create_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                exists = connection.execute(
                    "SELECT 1 FROM gemini_keys WHERE key_id = ?",
                    (key_id,),
                ).fetchone()
                if exists is None:
                    connection.rollback()
                    raise StorageError("Gemini key metadata not found.")
                connection.execute("UPDATE gemini_keys SET is_active = 0")
                connection.execute(
                    "UPDATE gemini_keys SET is_active = 1 WHERE key_id = ?",
                    (key_id,),
                )
                connection.commit()
                row = connection.execute(
                    "SELECT * FROM gemini_keys WHERE key_id = ?",
                    (key_id,),
                ).fetchone()
                if row is None:
                    raise StorageError("Gemini key metadata not found after activation.")
                return self._row(row)
        except sqlite3.Error as exc:
            raise StorageError(f"Could not activate Gemini key metadata: {exc}") from exc

    def delete(self, key_id: str) -> None:
        if not self._db_path.is_file():
            return
        try:
            with self._connect() as connection:
                self._create_schema(connection)
                connection.execute("DELETE FROM gemini_keys WHERE key_id = ?", (key_id,))
                connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Could not delete Gemini key metadata: {exc}") from exc

    def _connect(self) -> sqlite3.Connection:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self._db_path)

    def _create_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS gemini_keys (
                key_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                masked_key TEXT NOT NULL,
                fingerprint TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                last_checked_at TEXT,
                is_active INTEGER NOT NULL,
                detail TEXT NOT NULL
            )
            """
        )

    @staticmethod
    def _row(row: sqlite3.Row) -> GeminiKeyProfile:
        checked = row["last_checked_at"]
        return GeminiKeyProfile(
            key_id=str(row["key_id"]),
            label=str(row["label"]),
            masked_key=str(row["masked_key"]),
            fingerprint=str(row["fingerprint"]),
            status=GeminiKeyStatus(str(row["status"])),
            last_checked_at=(datetime.fromisoformat(str(checked)) if checked is not None else None),
            is_active=bool(int(row["is_active"])),
            detail=str(row["detail"]),
        )
