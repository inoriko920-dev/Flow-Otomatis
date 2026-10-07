from __future__ import annotations

import json
from pathlib import Path

from flow_otomatis.application.ports.google_session import GoogleSessionState
from flow_otomatis.workers.browser.google_session_worker import (
    BrowserSessionProbe,
    GoogleSessionWorker,
)


class FixtureBrowserDriver:
    def __init__(self) -> None:
        self.state = GoogleSessionState.NEEDS_LOGIN
        self.opened: list[str] = []
        self.closed: list[str] = []

    def open_login(
        self,
        profile_id: str,
        user_data_dir: Path,
        *,
        timeout_ms: int,
    ) -> BrowserSessionProbe:
        assert timeout_ms > 0
        assert user_data_dir.name == "browser-data"
        self.opened.append(profile_id)
        return BrowserSessionProbe(
            GoogleSessionState.NEEDS_LOGIN,
            "Login manual diperlukan.",
        )

    def check(
        self,
        profile_id: str,
        user_data_dir: Path,
        *,
        timeout_ms: int,
    ) -> BrowserSessionProbe:
        assert profile_id
        assert timeout_ms > 0
        assert user_data_dir.name == "browser-data"
        return BrowserSessionProbe(self.state, "Fixture status aman.")

    def close(self, profile_id: str) -> None:
        self.closed.append(profile_id)

    def shutdown(self) -> None:
        self.closed.append("shutdown")


def test_google_session_worker_persists_only_safe_metadata(tmp_path: Path) -> None:
    driver = FixtureBrowserDriver()
    session_root = tmp_path / "Sessions"
    worker = GoogleSessionWorker(
        session_root,
        tmp_path / "runtime" / "browsers",
        driver=driver,
    )

    profile = worker.create_profile("Akun Produksi Saya")
    opened = worker.open_login(profile.profile_id)
    assert opened.state is GoogleSessionState.NEEDS_LOGIN
    assert driver.opened == [profile.profile_id]

    driver.state = GoogleSessionState.READY
    checked = worker.check_profile(profile.profile_id)
    assert checked.state is GoogleSessionState.READY
    assert checked.last_checked_at is not None

    metadata_path = session_root / "google" / profile.profile_id / "profile.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert set(payload) == {
        "profile_id",
        "label",
        "state",
        "last_checked_at",
        "detail",
    }
    serialized = json.dumps(payload).casefold()
    for forbidden in ("password", "cookie", "token", "credential"):
        assert forbidden not in serialized

    reloaded = GoogleSessionWorker(
        session_root,
        tmp_path / "runtime" / "browsers",
        driver=driver,
    ).list_profiles()
    assert len(reloaded) == 1
    assert reloaded[0].state is GoogleSessionState.READY


def test_google_session_worker_cancel_and_delete_are_profile_scoped(tmp_path: Path) -> None:
    driver = FixtureBrowserDriver()
    worker = GoogleSessionWorker(
        tmp_path / "Sessions",
        tmp_path / "runtime" / "browsers",
        driver=driver,
    )
    first = worker.create_profile("Akun 1")
    second = worker.create_profile("Akun 2")

    worker.cancel_profile(first.profile_id)
    assert driver.closed == [first.profile_id]

    worker.delete_profile(first.profile_id)
    remaining = worker.list_profiles()
    assert [profile.profile_id for profile in remaining] == [second.profile_id]
    assert driver.closed[-1] == first.profile_id


def test_restart_gate_requires_ready_on_a_new_app_instance(tmp_path: Path) -> None:
    driver = FixtureBrowserDriver()
    driver.state = GoogleSessionState.READY
    session_root = tmp_path / "Sessions"

    first_worker = GoogleSessionWorker(
        session_root,
        tmp_path / "runtime" / "browsers",
        driver=driver,
        instance_id="app-instance-a",
    )
    profile = first_worker.create_profile("Akun Restart")
    first_worker.check_profile(profile.profile_id)

    first_gate = first_worker.get_restart_gate(profile.profile_id)
    assert first_gate.current_state is GoogleSessionState.READY
    assert first_gate.first_ready_at is not None
    assert first_gate.restart_verified_at is None
    assert first_gate.ready_after_restart is False

    same_instance_gate = first_worker.get_restart_gate(profile.profile_id)
    assert same_instance_gate.ready_after_restart is False

    second_worker = GoogleSessionWorker(
        session_root,
        tmp_path / "runtime" / "browsers",
        driver=driver,
        instance_id="app-instance-b",
    )
    second_worker.check_profile(profile.profile_id)

    restarted_gate = second_worker.get_restart_gate(profile.profile_id)
    assert restarted_gate.current_state is GoogleSessionState.READY
    assert restarted_gate.restart_verified_at is not None
    assert restarted_gate.ready_after_restart is True


def test_restart_proof_contains_only_sanitized_metadata(tmp_path: Path) -> None:
    driver = FixtureBrowserDriver()
    driver.state = GoogleSessionState.READY
    session_root = tmp_path / "Sessions"
    worker = GoogleSessionWorker(
        session_root,
        tmp_path / "runtime" / "browsers",
        driver=driver,
        instance_id="app-instance-a",
    )
    profile = worker.create_profile("Akun Aman")
    worker.check_profile(profile.profile_id)

    proof_path = session_root / "google" / profile.profile_id / "restart-proof.json"
    payload = json.loads(proof_path.read_text(encoding="utf-8"))
    assert set(payload) == {
        "first_ready_instance_id",
        "first_ready_at",
        "restart_verified_at",
    }
    serialized = json.dumps(payload).casefold()
    for forbidden in ("password", "cookie", "token", "credential", "browser-data"):
        assert forbidden not in serialized


def test_restart_gate_requires_current_ready_state(tmp_path: Path) -> None:
    driver = FixtureBrowserDriver()
    session_root = tmp_path / "Sessions"
    first_worker = GoogleSessionWorker(
        session_root,
        tmp_path / "runtime" / "browsers",
        driver=driver,
        instance_id="app-instance-a",
    )
    profile = first_worker.create_profile("Akun Expired")
    driver.state = GoogleSessionState.READY
    first_worker.check_profile(profile.profile_id)

    second_worker = GoogleSessionWorker(
        session_root,
        tmp_path / "runtime" / "browsers",
        driver=driver,
        instance_id="app-instance-b",
    )
    second_worker.check_profile(profile.profile_id)
    assert second_worker.get_restart_gate(profile.profile_id).ready_after_restart is True

    driver.state = GoogleSessionState.NEEDS_LOGIN
    second_worker.check_profile(profile.profile_id)
    gate = second_worker.get_restart_gate(profile.profile_id)
    assert gate.restart_verified_at is not None
    assert gate.current_state is GoogleSessionState.NEEDS_LOGIN
    assert gate.ready_after_restart is False
