from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from flow_otomatis.application.ports.gemini_keys import GeminiKeyHealthEvidence
from flow_otomatis.application.services.gemini_keys import GeminiKeyService
from flow_otomatis.domain.errors import FlowOtomatisError
from flow_otomatis.domain.gemini import GeminiKeyStatus
from flow_otomatis.infrastructure.persistence import SqliteGeminiKeyRepository


class MemorySecrets:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def set_secret(self, key_id: str, secret: str) -> None:
        self.values[key_id] = secret

    def get_secret(self, key_id: str) -> str | None:
        return self.values.get(key_id)

    def delete_secret(self, key_id: str) -> None:
        self.values.pop(key_id, None)


class FakeHealth:
    def __init__(self, status: GeminiKeyStatus = GeminiKeyStatus.VALID) -> None:
        self.status = status
        self.calls: list[str] = []

    def check(self, api_key: str) -> GeminiKeyHealthEvidence:
        self.calls.append(api_key)
        return GeminiKeyHealthEvidence(
            status=self.status,
            detail=f"fixture {self.status.value.lower()}",
        )


def _service(tmp_path: Path, health: FakeHealth | None = None):
    repo = SqliteGeminiKeyRepository(tmp_path / "settings" / "gemini_keys.sqlite3")
    secrets = MemorySecrets()
    checker = health or FakeHealth()
    return repo, secrets, checker, GeminiKeyService(repo, secrets, checker)


def test_import_masks_keys_deduplicates_and_keeps_raw_secret_out_of_sqlite(tmp_path: Path) -> None:
    repo, secrets, _health, service = _service(tmp_path)
    first = "A" * 36 + "1234"
    second = "B" * 36 + "5678"

    summary = service.import_text(f"Gemini Utama | {first}\nGemini Cadangan | {second}\n{first}\n")

    assert len(summary.imported) == 2
    assert summary.duplicate_count == 1
    profiles = service.list_profiles()
    assert profiles[0].is_active is True
    assert profiles[0].masked_key.endswith("1234")
    assert profiles[1].masked_key.endswith("5678")
    assert first not in repr(profiles)
    assert second not in repr(profiles)
    assert set(secrets.values.values()) == {first, second}

    db_bytes = (tmp_path / "settings" / "gemini_keys.sqlite3").read_bytes()
    assert first.encode() not in db_bytes
    assert second.encode() not in db_bytes
    assert repo.find_by_fingerprint(profiles[0].fingerprint) is not None


def test_health_updates_metadata_and_manual_activation_never_rotates_automatically(
    tmp_path: Path,
) -> None:
    health = FakeHealth(GeminiKeyStatus.VALID)
    _repo, _secrets, checker, service = _service(tmp_path, health)
    first = "A" * 40
    second = "B" * 40
    service.import_text(f"First | {first}\nSecond | {second}")

    profiles = service.list_profiles()
    first_profile = next(profile for profile in profiles if profile.label == "First")
    second_profile = next(profile for profile in profiles if profile.label == "Second")
    assert first_profile.is_active is True
    assert second_profile.is_active is False

    checked = service.check_health(second_profile.key_id)
    assert checked.status is GeminiKeyStatus.VALID
    assert checked.last_checked_at is not None
    assert checker.calls == [second]
    assert next(
        profile for profile in service.list_profiles() if profile.label == "First"
    ).is_active

    service.set_active(second_profile.key_id)
    active = [profile for profile in service.list_profiles() if profile.is_active]
    assert [profile.label for profile in active] == ["Second"]


def test_invalid_key_cannot_be_manually_activated(tmp_path: Path) -> None:
    repo, _secrets, _checker, service = _service(tmp_path)
    service.import_text(f"Only | {'A' * 40}")
    profile = service.list_profiles()[0]
    repo.save(replace(profile, status=GeminiKeyStatus.INVALID, is_active=False))

    with pytest.raises(FlowOtomatisError, match="ditolak"):
        service.set_active(profile.key_id)


def test_active_secret_requires_valid_health_when_requested(tmp_path: Path) -> None:
    _repo, _secrets, _checker, service = _service(tmp_path)
    raw = "Z" * 40
    service.import_text(raw)

    with pytest.raises(FlowOtomatisError, match="Cek Health"):
        service.get_active_secret()

    profile = service.list_profiles()[0]
    service.check_health(profile.key_id)
    active, secret = service.get_active_secret()
    assert active.key_id == profile.key_id
    assert secret == raw
