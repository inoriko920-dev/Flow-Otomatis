from __future__ import annotations

import pytest

from flow_otomatis.application.ports import (
    GenerationAuthenticationRequiredError,
    GenerationCancelledError,
    GenerationProviderError,
    GenerationRequest,
    GenerationSubmissionAmbiguousError,
)
from flow_otomatis.workers.browser import (
    GoogleFlowGenerationProvider,
    GoogleFlowSubmitEvidence,
    GoogleFlowSubmitState,
)


class FixtureFlowDriver:
    def __init__(self, evidence: GoogleFlowSubmitEvidence) -> None:
        self.evidence = evidence
        self.calls: list[tuple[str, GenerationRequest, int]] = []

    def submit_one(
        self,
        profile_id: str,
        request: GenerationRequest,
        *,
        timeout_ms: int,
    ) -> GoogleFlowSubmitEvidence:
        self.calls.append((profile_id, request, timeout_ms))
        return self.evidence


def _request() -> GenerationRequest:
    return GenerationRequest(
        episode_id="EP500_FLOW",
        scene_id="SCENE_001",
        image_file="SCENE_001.png",
        motion_prompt="Slow cinematic push-in.",
        target_duration_s=3.8,
        flow_duration_s=4,
        model="Omni Flash 1.1",
        resolution="720p",
        aspect_ratio="16:9",
    )


def test_google_flow_contract_accepts_exactly_one_stable_submit() -> None:
    driver = FixtureFlowDriver(
        GoogleFlowSubmitEvidence(
            state=GoogleFlowSubmitState.ACCEPTED,
            detail="Accepted.",
            remote_result_id="flow-result-001",
        )
    )
    provider = GoogleFlowGenerationProvider("profile-0123456789ab", driver, timeout_ms=45000)

    result = provider.generate(_request())

    assert result.remote_result_id == "flow-result-001"
    assert len(driver.calls) == 1
    assert driver.calls[0][0] == "profile-0123456789ab"
    assert driver.calls[0][2] == 45000


@pytest.mark.parametrize(
    ("state", "error_type"),
    [
        (GoogleFlowSubmitState.AMBIGUOUS, GenerationSubmissionAmbiguousError),
        (GoogleFlowSubmitState.AUTH_REQUIRED, GenerationAuthenticationRequiredError),
        (GoogleFlowSubmitState.CANCELLED, GenerationCancelledError),
        (GoogleFlowSubmitState.SAFE_FAILURE, GenerationProviderError),
    ],
)
def test_google_flow_contract_maps_non_success_without_retry(
    state: GoogleFlowSubmitState,
    error_type: type[GenerationProviderError],
) -> None:
    driver = FixtureFlowDriver(GoogleFlowSubmitEvidence(state=state, detail=f"{state} fixture"))
    provider = GoogleFlowGenerationProvider("profile-0123456789ab", driver)

    with pytest.raises(error_type):
        provider.generate(_request())

    assert len(driver.calls) == 1


def test_accepted_without_stable_remote_id_is_ambiguous() -> None:
    driver = FixtureFlowDriver(
        GoogleFlowSubmitEvidence(
            state=GoogleFlowSubmitState.ACCEPTED,
            detail="UI looked accepted but no stable id exists.",
        )
    )
    provider = GoogleFlowGenerationProvider("profile-0123456789ab", driver)

    with pytest.raises(GenerationSubmissionAmbiguousError):
        provider.generate(_request())

    assert len(driver.calls) == 1
