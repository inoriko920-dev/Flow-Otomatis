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
