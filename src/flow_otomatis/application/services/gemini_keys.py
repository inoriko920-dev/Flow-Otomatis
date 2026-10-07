"""Gemini key vault/import/health orchestration."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from uuid import uuid4

from flow_otomatis.application.ports.gemini_keys import (
    GeminiKeyHealthProbePort,
    GeminiKeyVaultPort,
)
from flow_otomatis.domain.errors import FlowOtomatisError, InternalInvariantError
from flow_otomatis.domain.gemini_key import (
    GeminiKeyImportItem,
    GeminiKeyImportPreview,
    GeminiKeyImportStatus,
    GeminiKeySummary,
)


@dataclass(frozen=True, slots=True)
class _PendingGeminiKey:
    row_number: int
    label: str
    api_key: str
    masked_key: str
    fingerprint: str


class GeminiKeyService:
    """Keep raw Gemini keys out of presentation/persistence DTOs."""

    def __init__(
        self,
        vault: GeminiKeyVaultPort,
        health_probe: GeminiKeyHealthProbePort,
    ) -> None:
        self._vault = vault
        self._health_probe = health_probe
        self._pending: dict[str, tuple[_PendingGeminiKey, ...]] = {}

    def list_keys(self) -> tuple[GeminiKeySummary, ...]:
        """Return safe metadata in stable label order."""

        return tuple(sorted(self._vault.list_summaries(), key=lambda item: item.label.casefold()))

    def preview_import(self, text: str) -> GeminiKeyImportPreview:
        """Parse masked candidates while keeping raw keys only in ephemeral service memory."""

        existing = {summary.fingerprint for summary in self._vault.list_summaries()}
        seen = set(existing)
        preview_id = uuid4().hex
        pending: list[_PendingGeminiKey] = []
        items: list[GeminiKeyImportItem] = []

        for row_number, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            label, api_key = self._parse_line(line, row_number)
            if not self._structurally_valid(api_key):
                items.append(
                    GeminiKeyImportItem(
                        row_number=row_number,
                        label=label,
                        masked_key=self._mask(api_key),
                        status=GeminiKeyImportStatus.INVALID,
                    )
                )
                continue

            fingerprint = self._fingerprint(api_key)
            status = (
                GeminiKeyImportStatus.DUPLICATE
                if fingerprint in seen
                else GeminiKeyImportStatus.NEW
            )
            items.append(
                GeminiKeyImportItem(
                    row_number=row_number,
                    label=label,
                    masked_key=self._mask(api_key),
                    status=status,
                )
            )
            if status is GeminiKeyImportStatus.NEW:
                pending.append(
                    _PendingGeminiKey(
                        row_number=row_number,
                        label=label,
                        api_key=api_key,
                        masked_key=self._mask(api_key),
                        fingerprint=fingerprint,
                    )
                )
                seen.add(fingerprint)

        if not items:
            raise FlowOtomatisError("Tidak ada kandidat Gemini key pada input.")

        self._pending[preview_id] = tuple(pending)
        return GeminiKeyImportPreview(preview_id=preview_id, items=tuple(items))

    def commit_import(self, preview_id: str) -> tuple[GeminiKeySummary, ...]:
        """Persist only NEW candidates from one still-valid in-memory preview."""

        pending = self._pending.pop(preview_id, None)
        if pending is None:
            raise FlowOtomatisError("Preview impor Gemini key sudah kedaluwarsa atau tidak dikenal.")

        saved: list[GeminiKeySummary] = []
        for candidate in pending:
            key_id = f"gemini_{candidate.fingerprint[:16]}"
            saved.append(
                self._vault.save_key(
                    key_id=key_id,
                    label=candidate.label,
                    api_key=candidate.api_key,
                    masked_key=candidate.masked_key,
                    fingerprint=candidate.fingerprint,
                )
            )
        return tuple(saved)

    def discard_import(self, preview_id: str) -> None:
        """Forget raw in-memory candidates without persisting them."""

        self._pending.pop(preview_id, None)

    def activate(self, key_id: str) -> GeminiKeySummary:
        """Explicitly choose one key; health/rate-limit events never auto-switch it."""

        return self._vault.set_active(key_id)

    def check_health(self, key_id: str) -> GeminiKeySummary:
        """Probe one key without generating content and persist only sanitized status."""

        secret = self._vault.get_secret(key_id)
        result = self._health_probe.check(secret)
        return self._vault.update_health(key_id, result.state, result.detail[:300])

    def check_all_health(self) -> tuple[GeminiKeySummary, ...]:
        """Sequentially health-check all keys; never change the active selection."""

        before = {item.key_id: item.active for item in self._vault.list_summaries()}
        for summary in self.list_keys():
            self.check_health(summary.key_id)
        after = self.list_keys()
        if {item.key_id: item.active for item in after} != before:
            raise InternalInvariantError("Gemini health check changed active key selection")
        return after

    def get_active_secret(self) -> tuple[GeminiKeySummary, str]:
        """Return the explicitly active secret for an application/provider adapter."""

        active = [summary for summary in self._vault.list_summaries() if summary.active]
        if len(active) != 1:
            raise FlowOtomatisError("Pilih tepat satu Gemini key aktif terlebih dahulu.")
        summary = active[0]
        return summary, self._vault.get_secret(summary.key_id)

    def delete_key(self, key_id: str) -> None:
        """Delete one key; no replacement key is selected automatically."""

        self._vault.delete_key(key_id)

    @staticmethod
    def _parse_line(line: str, row_number: int) -> tuple[str, str]:
        if "\t" in line:
            label, api_key = line.split("\t", 1)
            normalized_label = " ".join(label.split())
            return normalized_label or f"Gemini Key {row_number:02d}", api_key.strip()
        return f"Gemini Key {row_number:02d}", line

    @staticmethod
    def _structurally_valid(api_key: str) -> bool:
        return 8 <= len(api_key) <= 512 and not any(char.isspace() for char in api_key)

    @staticmethod
    def _fingerprint(api_key: str) -> str:
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    @staticmethod
    def _mask(api_key: str) -> str:
        suffix = api_key[-4:] if len(api_key) >= 4 else "••••"
        return f"••••••••••{suffix}"
