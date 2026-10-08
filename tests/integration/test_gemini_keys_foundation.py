from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Event, Lock
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

class BlockingHealth:
    def __init__(self) -> None:
        self.entered = Event()
        self.release = Event()

    def check(self, api_key: str) -> GeminiKeyHealthEvidence:
        assert api_key
        self.entered.set()
        assert self.release.wait(5), "health barrier was never released"
        return GeminiKeyHealthEvidence(status=GeminiKeyStatus.VALID, detail="checked")


@pytest.mark.parametrize("target", ["First", "Second"])
def test_t01_t02_health_completion_never_changes_newer_manual_selection(
    tmp_path: Path, target: str,
) -> None:
    health = BlockingHealth()
    repo, _secrets, _checker, service = _service(tmp_path, health)
    service.import_text(f"First | {'A' * 40}\nSecond | {'B' * 40}")
    first, second = (next(p for p in service.list_profiles() if p.label == name)
                     for name in ("First", "Second"))
    checked = first if target == "First" else second

    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(service.check_health, checked.key_id)
        assert health.entered.wait(5)
        service.set_active(second.key_id)
        health.release.set()
        result = pending.result(timeout=5)

    assert result.status is GeminiKeyStatus.VALID
    assert result.is_active is (target == "Second")
    assert [p.key_id for p in repo.list_profiles() if p.is_active] == [second.key_id]


def test_t03_deleted_key_is_not_resurrected_by_health_completion(tmp_path: Path) -> None:
    health = BlockingHealth()
    repo, _secrets, _checker, service = _service(tmp_path, health)
    service.import_text(f"Deleted | {'A' * 40}")
    key_id = service.list_profiles()[0].key_id

    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(service.check_health, key_id)
        assert health.entered.wait(5)
        service.delete(key_id)
        health.release.set()
        with pytest.raises(FlowOtomatisError, match="dihapus"):
            pending.result(timeout=5)

    assert repo.get(key_id) is None
    assert repo.list_profiles() == ()


class ReversedHealth:
    def __init__(self) -> None:
        self.lock = Lock()
        self.count = 0
        self.started = [Event(), Event()]
        self.release = [Event(), Event()]

    def check(self, api_key: str) -> GeminiKeyHealthEvidence:
        assert api_key
        with self.lock:
            index = self.count
            self.count += 1
        self.started[index].set()
        assert self.release[index].wait(5), "health barrier was never released"
        status = GeminiKeyStatus.VALID if index == 0 else GeminiKeyStatus.INVALID
        return GeminiKeyHealthEvidence(status=status, detail=f"result-{index}")


def test_t04_late_old_health_result_cannot_replace_newer_completion(tmp_path: Path) -> None:
    health = ReversedHealth()
    repo, _secrets, _checker, service = _service(tmp_path, health)
    service.import_text(f"Only | {'A' * 40}")
    key_id = service.list_profiles()[0].key_id

    with ThreadPoolExecutor(max_workers=2) as pool:
        older = pool.submit(service.check_health, key_id)
        assert health.started[0].wait(5)
        newer = pool.submit(service.check_health, key_id)
        assert health.started[1].wait(5)
        health.release[1].set()
        assert newer.result(timeout=5).status is GeminiKeyStatus.INVALID
        health.release[0].set()
        assert older.result(timeout=5).status is GeminiKeyStatus.INVALID

    saved = repo.get(key_id)
    assert saved is not None
    assert saved.status is GeminiKeyStatus.INVALID
    assert saved.detail == "result-1"

