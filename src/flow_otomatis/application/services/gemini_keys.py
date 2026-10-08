"""Gemini key import, masking, health, and manual activation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock

from flow_otomatis.application.ports.gemini_keys import (
    GeminiKeyHealthPort,
    GeminiKeyRepositoryPort,
    SecretStorePort,
)
from flow_otomatis.domain.errors import FlowOtomatisError, InternalInvariantError
from flow_otomatis.domain.gemini import GeminiKeyProfile, GeminiKeyStatus

_MAX_KEYS = 100


@dataclass(frozen=True, slots=True)
class GeminiKeyImportSummary:
    """Safe import summary; raw keys are never returned."""

    imported: tuple[GeminiKeyProfile, ...]
    duplicate_count: int
    rejected_count: int


class GeminiKeyService:
    """Manage up to 100 user-owned Gemini keys without automatic rotation."""

    def __init__(
        self,
        repository: GeminiKeyRepositoryPort,
        secret_store: SecretStorePort,
        health: GeminiKeyHealthPort,
    ) -> None:
        self._repository = repository
        self._secret_store = secret_store
        self._health = health
        self._health_lock = Lock()
        self._health_request_versions: dict[str, int] = {}

    def list_profiles(self) -> tuple[GeminiKeyProfile, ...]:
        return self._repository.list_profiles()

    def import_text(self, text: str) -> GeminiKeyImportSummary:
        """Import plain or label|key lines; duplicates are skipped safely."""

        parsed = self._parse_lines(text)
        existing = self._repository.list_profiles()
        known = {profile.fingerprint for profile in existing}
        available = max(_MAX_KEYS - len(existing), 0)
        imported: list[GeminiKeyProfile] = []
        duplicates = 0
        rejected = 0

        for label, secret in parsed:
            fingerprint = hashlib.sha256(secret.encode("utf-8")).hexdigest()
            if fingerprint in known:
                duplicates += 1
                continue
            if available <= 0:
                rejected += 1
                continue
            key_id = f"gemini_{fingerprint[:20]}"
            profile = GeminiKeyProfile(
                key_id=key_id,
                label=label or f"Gemini Key {len(existing) + len(imported) + 1:02d}",
                masked_key=self._mask(secret),
                fingerprint=fingerprint,
                status=GeminiKeyStatus.UNCHECKED,
                last_checked_at=None,
                is_active=not any(item.is_active for item in (*existing, *imported)),
                detail="Belum dicek.",
            )
            self._secret_store.set_secret(key_id, secret)
            try:
                self._repository.save(profile)
            except Exception:
                self._secret_store.delete_secret(key_id)
                raise
            imported.append(profile)
            known.add(fingerprint)
            available -= 1

        if not imported and not duplicates and rejected == 0:
            raise FlowOtomatisError("Tidak ada Gemini API key yang valid untuk diimpor.")
        return GeminiKeyImportSummary(
            imported=tuple(imported),
            duplicate_count=duplicates,
            rejected_count=rejected,
        )

    def check_health(self, key_id: str) -> GeminiKeyProfile:
        """Patch health only; newest request wins without changing manual selection."""

        self._required_profile(key_id)
        with self._health_lock:
            version = self._health_request_versions.get(key_id, 0) + 1
            self._health_request_versions[key_id] = version

        secret = self._secret_store.get_secret(key_id)
        if not secret:
            status = GeminiKeyStatus.ERROR
            detail = "Secret key tidak ditemukan di penyimpanan aman OS."
        else:
            evidence = self._health.check(secret)
            status = evidence.status
            detail = evidence.detail[:300]

        checked_at = datetime.now(UTC)
        with self._health_lock:
            if self._health_request_versions[key_id] != version:
                current = self._repository.get(key_id)
                if current is None:
                    raise FlowOtomatisError("Gemini key sudah dihapus saat Cek Health.")
                return current

            updated = self._repository.update_health(key_id, status, checked_at, detail)
            if updated is None:
                raise FlowOtomatisError("Gemini key sudah dihapus saat Cek Health.")
            return updated

    def set_active(self, key_id: str) -> GeminiKeyProfile:
        """Select one key manually; never rotate automatically."""

        profile = self._required_profile(key_id)
        if profile.status is GeminiKeyStatus.INVALID:
            raise FlowOtomatisError("Key yang ditolak Gemini API tidak dapat diaktifkan.")
        return self._repository.set_active(key_id)

    def delete(self, key_id: str) -> None:
        """Delete the OS secret first, then remove credential-free metadata."""

        self._required_profile(key_id)
        self._secret_store.delete_secret(key_id)
        self._repository.delete(key_id)

    def get_active_secret(self, *, require_valid: bool = True) -> tuple[GeminiKeyProfile, str]:
        """Resolve the manually selected key only for a provider call."""

        active = next((profile for profile in self.list_profiles() if profile.is_active), None)
        if active is None:
            raise FlowOtomatisError("Belum ada Gemini key aktif.")
        if require_valid and active.status is not GeminiKeyStatus.VALID:
            raise FlowOtomatisError("Gemini key aktif harus lolos Cek Health terlebih dahulu.")
        secret = self._secret_store.get_secret(active.key_id)
        if not secret:
            raise InternalInvariantError("Gemini secret is missing from the OS secret store.")
        return active, secret

    def _required_profile(self, key_id: str) -> GeminiKeyProfile:
        profile = self._repository.get(key_id)
        if profile is None:
            raise FlowOtomatisError("Gemini key tidak ditemukan.")
        return profile

    @staticmethod
    def _mask(secret: str) -> str:
        tail = secret[-4:] if len(secret) >= 4 else secret
        return f"••••••••••{tail}"

    @staticmethod
    def _parse_lines(text: str) -> list[tuple[str, str]]:
        parsed: list[tuple[str, str]] = []
        for raw in text.splitlines():
            line = raw.strip().strip('"').strip("'")
            if not line:
                continue
            label = ""
            secret = line
            if "\t" in line:
                label, secret = (part.strip() for part in line.split("\t", 1))
            elif "|" in line:
                label, secret = (part.strip() for part in line.split("|", 1))
            secret = secret.strip()
            if len(secret) < 20 or any(char.isspace() for char in secret):
                continue
            parsed.append((label[:80], secret))
        return parsed
