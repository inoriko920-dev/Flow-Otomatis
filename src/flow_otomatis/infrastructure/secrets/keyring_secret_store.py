"""OS keyring-backed secret storage for Gemini API keys."""

from __future__ import annotations

import keyring
from keyring.errors import KeyringError, PasswordDeleteError

from flow_otomatis.domain.errors import StorageError

_SERVICE_NAME = "Flow-Otomatis/Gemini"


class KeyringSecretStore:
    """Keep Gemini API keys in the OS credential store, never in project SQLite."""

    def set_secret(self, key_id: str, secret: str) -> None:
        try:
            keyring.set_password(_SERVICE_NAME, key_id, secret)
        except KeyringError as exc:
            raise StorageError("Penyimpanan aman OS gagal menyimpan Gemini key.") from exc

    def get_secret(self, key_id: str) -> str | None:
        try:
            return keyring.get_password(_SERVICE_NAME, key_id)
        except KeyringError as exc:
            raise StorageError("Penyimpanan aman OS gagal membaca Gemini key.") from exc

    def delete_secret(self, key_id: str) -> None:
        try:
            keyring.delete_password(_SERVICE_NAME, key_id)
        except PasswordDeleteError:
            return
        except KeyringError as exc:
            raise StorageError("Penyimpanan aman OS gagal menghapus Gemini key.") from exc
