from __future__ import annotations

from pathlib import Path

import pytest

from flow_otomatis.application.ports import GoogleFlowAccessState
from flow_otomatis.domain.errors import FlowOtomatisError
from flow_otomatis.workers.browser import GoogleFlowPreflightWorker


class FixturePreflightDriver:
    def __init__(self, state: GoogleFlowAccessState) -> None:
        self.state = state
        self.calls: list[tuple[str, Path, int]] = []
        self.closed: list[str] = []

    def check(
        self,
        profile_id: str,
        user_data_dir: Path,
        *,
        timeout_ms: int,
    ) -> tuple[GoogleFlowAccessState, str]:
        self.calls.append((profile_id, user_data_dir, timeout_ms))
        return self.state, f"{self.state.value} fixture"

    def close(self, profile_id: str) -> None:
        self.closed.append(profile_id)

    def shutdown(self) -> None:
        self.closed.append("shutdown")


def _profile_root(tmp_path: Path, profile_id: str) -> Path:
    root = tmp_path / "Sessions" / "google" / profile_id
    root.mkdir(parents=True)
    (root / "profile.json").write_text("{}", encoding="utf-8")
    return root


@pytest.mark.parametrize(
    "state",
    [
        GoogleFlowAccessState.REACHABLE,
        GoogleFlowAccessState.AUTH_REQUIRED,
        GoogleFlowAccessState.UNAVAILABLE,
        GoogleFlowAccessState.UNKNOWN,
        GoogleFlowAccessState.ERROR,
    ],
)
def test_read_only_flow_preflight_returns_sanitized_state(
    tmp_path: Path,
    state: GoogleFlowAccessState,
) -> None:
    profile_id = "profile-0123456789ab"
    root = _profile_root(tmp_path, profile_id)
    driver = FixturePreflightDriver(state)
    worker = GoogleFlowPreflightWorker(
        tmp_path / "Sessions",
        tmp_path / "runtime" / "browsers",
        driver=driver,
    )

    probe = worker.check(profile_id)

    assert probe.profile_id == profile_id
    assert probe.state is state
    assert probe.detail == f"{state.value} fixture"
    assert driver.calls == [(profile_id, root / "browser-data", 20000)]


def test_preflight_refuses_unknown_or_missing_local_profile(tmp_path: Path) -> None:
    driver = FixturePreflightDriver(GoogleFlowAccessState.REACHABLE)
    worker = GoogleFlowPreflightWorker(
        tmp_path / "Sessions",
        tmp_path / "runtime" / "browsers",
        driver=driver,
    )

    with pytest.raises(FlowOtomatisError):
        worker.check("../other-profile")

    with pytest.raises(FlowOtomatisError):
        worker.check("profile-0123456789ab")

    assert driver.calls == []
