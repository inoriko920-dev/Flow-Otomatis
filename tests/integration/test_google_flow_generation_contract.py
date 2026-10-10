from __future__ import annotations

import pytest

from flow_otomatis.application.ports import (
    GenerationAuthenticationRequiredError,
    GenerationCancelledError,
    GenerationProviderError,
    GenerationRequest,
    GenerationRequestValidationError,
    GenerationSafeFailureError,
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
        (GoogleFlowSubmitState.SAFE_FAILURE, GenerationSafeFailureError),
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


@pytest.mark.parametrize(
    ("changes", "message_fragment"),
    [
        ({"episode_id": "   "}, "episode_id"),
        ({"scene_id": ""}, "scene_id"),
        ({"image_file": " "}, "File gambar"),
        ({"motion_prompt": "   "}, "Motion prompt"),
        ({"target_duration_s": 0.0}, "lebih besar dari 0"),
        ({"flow_duration_s": 5}, "4, 6, 8, atau 10"),
        ({"target_duration_s": 7.0, "flow_duration_s": 6}, "sama atau lebih panjang"),
        ({"model": "Other model"}, "Model harus Omni Flash 1.1"),
        ({"resolution": "1080p"}, "Resolusi harus 720p"),
        ({"aspect_ratio": "9:16"}, "Aspect ratio harus 16:9"),
    ],
)
def test_invalid_request_fails_before_driver_mutation(
    changes: dict[str, object],
    message_fragment: str,
) -> None:
    base = _request()
    payload = {
        "episode_id": base.episode_id,
        "scene_id": base.scene_id,
        "image_file": base.image_file,
        "motion_prompt": base.motion_prompt,
        "target_duration_s": base.target_duration_s,
        "flow_duration_s": base.flow_duration_s,
        "model": base.model,
        "resolution": base.resolution,
        "aspect_ratio": base.aspect_ratio,
    }
    payload.update(changes)
    request = GenerationRequest(**payload)  # type: ignore[arg-type]
    driver = FixtureFlowDriver(
        GoogleFlowSubmitEvidence(
            state=GoogleFlowSubmitState.ACCEPTED,
            detail="This must never be reached.",
            remote_result_id="should-not-exist",
        )
    )
    provider = GoogleFlowGenerationProvider("profile-0123456789ab", driver)

    with pytest.raises(GenerationRequestValidationError, match=message_fragment):
        provider.generate(request)

    assert driver.calls == []


@pytest.mark.parametrize("state", [
    GoogleFlowSubmitState.SAFE_FAILURE,
    GoogleFlowSubmitState.AUTH_REQUIRED,
    GoogleFlowSubmitState.CANCELLED,
])
def test_t13_contradictory_result_id_never_proves_safe_failure(
    state: GoogleFlowSubmitState,
) -> None:
    driver = FixtureFlowDriver(
        GoogleFlowSubmitEvidence(
            state=state,
            detail="Authorization Bearer FAKE_SECRET_UNTRUSTED",
            remote_result_id="remote-id-contradicts-failure",
        )
    )
    provider = GoogleFlowGenerationProvider("profile-test", driver)
    with pytest.raises(GenerationSubmissionAmbiguousError) as error:
        provider.generate(_request())
    assert "FAKE_SECRET_UNTRUSTED" not in str(error.value)
    assert len(driver.calls) == 1


def test_t13_blank_safe_failure_evidence_is_ambiguous() -> None:
    driver = FixtureFlowDriver(
        GoogleFlowSubmitEvidence(
            state=GoogleFlowSubmitState.SAFE_FAILURE,
            detail="   ",
        )
    )
    with pytest.raises(GenerationSubmissionAmbiguousError):
        GoogleFlowGenerationProvider("profile-test", driver).generate(_request())
    assert len(driver.calls) == 1
