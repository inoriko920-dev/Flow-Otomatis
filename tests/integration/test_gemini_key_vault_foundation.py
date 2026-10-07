from __future__ import annotations

import json
from pathlib import Path

import pytest

from flow_otomatis.application.services.gemini_keys import GeminiKeyService
from flow_otomatis.domain.errors import FlowOtomatisError
from flow_otomatis.domain.gemini_key import (
    GeminiKeyHealthResult,
    GeminiKeyHealthState,
    GeminiKeyImportStatus,
)
from flow_otomatis.infrastructure.secrets import KeyringGeminiKeyVault


class FakeKeyring:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], str] = {}

    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.values[(service_name, username)] = password

    def get_password(self, service_name: str, username: str) -> str | None:
        return self.values.get((service_name, username))

    def delete_password(self, service_name: str, username: str) -> None:
        self.values.pop((service_name, username), None)


class FakeHealthProbe:
    def __init__(self, state: GeminiKeyHealthState = GeminiKeyHealthState.HEALTHY) -> None:
        self.state = state
        self.seen: list[str] = []

    def check(self, api_key: str) -> GeminiKeyHealthResult:
        self.seen.append(api_key)
        return GeminiKeyHealthResult(self.state, f"fixture {self.state.value.lower()}")


def _service(tmp_path: Path, *, state: GeminiKeyHealthState = GeminiKeyHealthState.HEALTHY):
    backend = FakeKeyring()
    registry = tmp_path / "GeminiKeys" / "registry.json"
    vault = KeyringGeminiKeyVault(registry, backend=backend)
    probe = FakeHealthProbe(state)
    return GeminiKeyService(vault, probe), backend, registry, probe


def test_import_preview_masks_raw_keys_and_detects_duplicates(tmp_path: Path) -> None:
    service, _backend, registry, _probe = _service(tmp_path)
    secret = "AIzaFixtureKeyAlpha1234"

    preview = service.preview_import(
        f"Utama\t{secret}\nCadangan\t{secret}\ninvalid key with spaces"
    )

    assert [item.status for item in preview.items] == [
        GeminiKeyImportStatus.NEW,
        GeminiKeyImportStatus.DUPLICATE,
        GeminiKeyImportStatus.INVALID,
    ]
    assert preview.new_count == 1
    assert preview.duplicate_count == 1
    assert preview.invalid_count == 1
    assert secret not in repr(preview)
    assert not registry.exists()


def test_commit_stores_secret_only_in_keyring_and_metadata_is_masked(tmp_path: Path) -> None:
    service, backend, registry, _probe = _service(tmp_path)
    secret = "AIzaFixtureKeyAlpha1234"

    preview = service.preview_import(f"Gemini Utama\t{secret}")
    saved = service.commit_import(preview.preview_id)

    assert len(saved) == 1
    summary = saved[0]
    assert summary.active is True
    assert summary.masked_key.endswith("1234")
    assert secret not in registry.read_text(encoding="utf-8")
    assert secret in backend.values.values()
    assert secret not in repr(summary)

    payload = json.loads(registry.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["keys"][0]["masked_key"].endswith("1234")


def test_active_key_changes_only_by_explicit_activation(tmp_path: Path) -> None:
    service, _backend, _registry, probe = _service(
        tmp_path,
        state=GeminiKeyHealthState.RATE_LIMITED,
    )
    preview = service.preview_import(
        "Utama\tAIzaFixtureKeyAlpha1234\nCadangan\tAIzaFixtureKeyBeta5678"
    )
    saved = service.commit_import(preview.preview_id)
    assert [item.active for item in service.list_keys()] == [False, True] or [
        item.active for item in service.list_keys()
    ] == [True, False]

    first_active = next(item for item in service.list_keys() if item.active)
    service.check_all_health()
    assert next(item for item in service.list_keys() if item.active).key_id == first_active.key_id
    assert len(probe.seen) == 2

    other = next(item for item in saved if item.key_id != first_active.key_id)
    selected = service.activate(other.key_id)
    assert selected.active is True
    assert next(item for item in service.list_keys() if item.active).key_id == other.key_id


def test_preview_is_one_time_and_raw_candidate_can_be_discarded(tmp_path: Path) -> None:
    service, backend, _registry, _probe = _service(tmp_path)
    preview = service.preview_import("AIzaFixtureKeyAlpha1234")
    service.discard_import(preview.preview_id)

    with pytest.raises(FlowOtomatisError, match="kedaluwarsa"):
        service.commit_import(preview.preview_id)

    assert backend.values == {}
