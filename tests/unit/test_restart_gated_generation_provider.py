from __future__ import annotations

from datetime import UTC, datetime

import pytest

from flow_otomatis.application.ports.generation_provider import (
    GenerationAuthenticationRequiredError,
    GenerationProviderResult,
    GenerationRequest,
)
from flow_otomatis.application.ports.google_session import (
    GoogleSessionProfile,
    GoogleSessionRestartGate,
    GoogleSessionState,
)
from flow_otomatis.application.services.google_sessions import GoogleSessionService
from flow_otomatis.application.services.restart_gated_generation import (
    RestartGatedGenerationProvider,
)


class FixtureSessionPort:
    def __init__(self, gate: GoogleSessionRestartGate) -> None:
        self.gate = gate
        self.gate_reads = 0

    def list_profiles(self) -> tuple[GoogleSessionProfile, ...]:
        return ()

    def create_profile(self, label: str) -> GoogleSessionProfile:
        raise AssertionError

    def open_login(self, profile_id: str) -> GoogleSessionProfile:
        raise AssertionError

    def check_profile(self, profile_id: str) -> GoogleSessionProfile:
        raise AssertionError

    def get_restart_gate(self, profile_id: str) -> GoogleSessionRestartGate:
        assert profile_id == self.gate.profile_id
        self.gate_reads += 1
        return self.gate

    def cancel_profile(self, profile_id: str) -> None:
        raise AssertionError

    def delete_profile(self, profile_id: str) -> None:
        raise AssertionError

    def shutdown(self) -> None:
        pass


class FixtureDownstreamProvider:
    def __init__(self) -> None:
        self.calls: list[GenerationRequest] = []

    def generate(self, request: GenerationRequest) -> GenerationProviderResult:
        self.calls.append(request)
        return GenerationProviderResult(remote_result_id="flow-result-guarded")


def _request() -> GenerationRequest:
    return GenerationRequest(
        episode_id="EP_GATE",
        scene_id="SCENE_001",
        image_file="SCENE_001.png",
        motion_prompt="Slow cinematic push-in.",
        target_duration_s=3.5,
        flow_duration_s=4,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
    )


def _gate(
    *,
    state: GoogleSessionState = GoogleSessionState.READY,
    verified: bool,
) -> GoogleSessionRestartGate:
    return GoogleSessionRestartGate(
        profile_id="profile-0123456789ab",
        current_state=state,
        first_ready_at=datetime(2026, 10, 7, 10, 0, tzinfo=UTC),
        restart_verified_at=(datetime(2026, 10, 7, 10, 5, tzinfo=UTC) if verified else None),
    )


@pytest.mark.parametrize(
    "gate",
    [
        _gate(verified=False),
        _gate(state=GoogleSessionState.NEEDS_LOGIN, verified=True),
        _gate(state=GoogleSessionState.UNKNOWN, verified=True),
        _gate(state=GoogleSessionState.ERROR, verified=True),
    ],
)
def test_generation_is_blocked_before_downstream_when_restart_gate_is_not_ready(
    gate: GoogleSessionRestartGate,
) -> None:
    port = FixtureSessionPort(gate)
    downstream = FixtureDownstreamProvider()
    provider = RestartGatedGenerationProvider(
        gate.profile_id,
        GoogleSessionService(port),
        downstream,
    )

    with pytest.raises(GenerationAuthenticationRequiredError, match="Validasi restart"):
        provider.generate(_request())

    assert port.gate_reads == 1
    assert downstream.calls == []


def test_generation_reaches_downstream_once_when_restart_gate_passes() -> None:
    gate = _gate(verified=True)
    port = FixtureSessionPort(gate)
    downstream = FixtureDownstreamProvider()
    provider = RestartGatedGenerationProvider(
        gate.profile_id,
        GoogleSessionService(port),
        downstream,
    )

    result = provider.generate(_request())

    assert result.remote_result_id == "flow-result-guarded"
    assert port.gate_reads == 1
    assert downstream.calls == [_request()]
