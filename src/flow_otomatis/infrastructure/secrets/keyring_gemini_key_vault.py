"""Windows/keyring-backed Gemini secret vault with credential-free JSON metadata."""

from __future__ import annotations

import json
import os
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import keyring

from flow_otomatis.domain.errors import StorageError
from flow_otomatis.domain.gemini_key import GeminiKeyHealthState, GeminiKeySummary

_SERVICE_NAME = "Flow-Otomatis/Gemini"


class _KeyringBackend(Protocol):
    def set_password(self, service_name: str, username: str, password: str) -> None: ...
    def get_password(self, service_name: str, username: str) -> str | None: ...
    def delete_password(self, service_name: str, username: str) -> None: ...


class KeyringGeminiKeyVault:
    """Keep full keys in OS keyring and only safe metadata in a local registry."""

    def __init__(
        self,
        registry_path: Path,
        *,
        backend: _KeyringBackend = keyring,
    ) -> None:
        self._registry_path = registry_path
        self._backend = backend

    def list_summaries(self) -> tuple[GeminiKeySummary, ...]:
        return tuple(self._decode(item) for item in self._read_registry())

    def save_key(
        self,
        *,
        key_id: str,
        label: str,
        api_key: str,
        masked_key: str,
        fingerprint: str,
    ) -> GeminiKeySummary:
        records = self._read_registry()
        if any(str(item["fingerprint"]) == fingerprint for item in records):
            raise StorageError("Gemini key sudah tersimpan.")

        self._backend.set_password(_SERVICE_NAME, key_id, api_key)
        now = datetime.now(UTC)
        record = {
            "key_id": key_id,
            "label": label,
            "masked_key": masked_key,
            "fingerprint": fingerprint,
            "active": not records,
            "health_state": GeminiKeyHealthState.UNCHECKED.value,
            "last_checked_at": None,
            "detail": "Belum dicek.",
            "created_at": now.isoformat(),
        }
        try:
            self._write_registry([*records, record])
        except Exception:
            with suppress(Exception):
                self._backend.delete_password(_SERVICE_NAME, key_id)
            raise
        return self._decode(record)

    def get_secret(self, key_id: str) -> str:
        if not any(str(item["key_id"]) == key_id for item in self._read_registry()):
            raise StorageError("Gemini key tidak ditemukan.")
        value = self._backend.get_password(_SERVICE_NAME, key_id)
        if value is None:
            raise StorageError("Secret Gemini key tidak tersedia di credential store.")
        return value

    def set_active(self, key_id: str) -> GeminiKeySummary:
        records = self._read_registry()
        if not any(str(item["key_id"]) == key_id for item in records):
            raise StorageError("Gemini key tidak ditemukan.")
        updated = [{**item, "active": str(item["key_id"]) == key_id} for item in records]
        self._write_registry(updated)
        selected = next(item for item in updated if str(item["key_id"]) == key_id)
        return self._decode(selected)

    def update_health(
        self,
        key_id: str,
        state: GeminiKeyHealthState,
        detail: str,
    ) -> GeminiKeySummary:
        records = self._read_registry()
        found = False
        checked_at = datetime.now(UTC).isoformat()
        updated: list[dict[str, object]] = []
        for item in records:
            if str(item["key_id"]) == key_id:
                item = {
                    **item,
                    "health_state": state.value,
                    "last_checked_at": checked_at,
                    "detail": detail,
                }
                found = True
            updated.append(item)
        if not found:
            raise StorageError("Gemini key tidak ditemukan.")
        self._write_registry(updated)
        selected = next(item for item in updated if str(item["key_id"]) == key_id)
        return self._decode(selected)

    def delete_key(self, key_id: str) -> None:
        records = self._read_registry()
        target = [item for item in records if str(item["key_id"]) == key_id]
        if not target:
            raise StorageError("Gemini key tidak ditemukan.")
        remaining = [item for item in records if str(item["key_id"]) != key_id]
        self._backend.delete_password(_SERVICE_NAME, key_id)
        self._write_registry(remaining)

    def _read_registry(self) -> list[dict[str, object]]:
        if not self._registry_path.is_file():
            return []
        try:
            payload = json.loads(self._registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError("Registry metadata Gemini key tidak dapat dibaca.") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list):
            raise StorageError("Format registry metadata Gemini key tidak valid.")
        records = payload["keys"]
        if not all(isinstance(item, dict) for item in records):
            raise StorageError("Format record metadata Gemini key tidak valid.")
        return [dict(item) for item in records]

    def _write_registry(self, records: list[dict[str, object]]) -> None:
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._registry_path.with_suffix(".tmp")
        payload = {"schema_version": 1, "keys": records}
        try:
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            os.replace(temporary, self._registry_path)
        except OSError as exc:
            temporary.unlink(missing_ok=True)
            raise StorageError("Registry metadata Gemini key tidak dapat disimpan.") from exc

    @staticmethod
    def _decode(item: dict[str, object]) -> GeminiKeySummary:
        checked_raw = item.get("last_checked_at")
        return GeminiKeySummary(
            key_id=str(item["key_id"]),
            label=str(item["label"]),
            masked_key=str(item["masked_key"]),
            fingerprint=str(item["fingerprint"]),
            active=bool(item["active"]),
            health_state=GeminiKeyHealthState(str(item["health_state"])),
            last_checked_at=(
                datetime.fromisoformat(str(checked_raw)) if checked_raw is not None else None
            ),
            detail=str(item.get("detail", "")),
        )
