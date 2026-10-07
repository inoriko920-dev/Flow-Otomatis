from __future__ import annotations

import pytest

from flow_otomatis.application.ports import (
    GenerationRequest,
    GenerationRequestValidationError,
)
from flow_otomatis.workers.browser import prepare_google_flow_request


def test_prepare_google_flow_request_normalizes_frozen_settings() -> None:
    prepared = prepare_google_flow_request(
        GenerationRequest(
            episode_id=" EP600 ",
            scene_id=" SCENE_010 ",
            image_file=" image.png ",
            motion_prompt=" Camera slowly moves forward. ",
            target_duration_s=7.1,
            flow_duration_s=8,
            model=" Omni Flash 1.1 ",
            resolution=" 720p ",
            aspect_ratio=" 16:9 ",
        )
    )

    assert prepared.episode_id == "EP600"
    assert prepared.scene_id == "SCENE_010"
    assert prepared.image_file == "image.png"
    assert prepared.motion_prompt == "Camera slowly moves forward."
    assert prepared.flow_duration_s == 8
    assert prepared.model == "Omni Flash 1.1"
    assert prepared.resolution == "720p"
    assert prepared.aspect_ratio == "16:9"


@pytest.mark.parametrize("duration", [4, 6, 8, 10])
def test_only_frozen_flow_duration_values_are_accepted(duration: int) -> None:
    prepared = prepare_google_flow_request(
        GenerationRequest(
            episode_id="EP600",
            scene_id="SCENE_010",
            image_file="image.png",
            motion_prompt="Move.",
            target_duration_s=float(duration),
            flow_duration_s=duration,
            model="Omni Flash 1.1",
            resolution="720p",
            aspect_ratio="16:9",
        )
    )

    assert prepared.flow_duration_s == duration


def test_scene_over_flow_duration_is_rejected_before_browser() -> None:
    with pytest.raises(GenerationRequestValidationError, match="pecah Scene >10 detik"):
        prepare_google_flow_request(
            GenerationRequest(
                episode_id="EP600",
                scene_id="SCENE_010",
                image_file="image.png",
                motion_prompt="Move.",
                target_duration_s=10.1,
                flow_duration_s=10,
                model="Omni Flash 1.1",
                resolution="720p",
                aspect_ratio="16:9",
            )
        )
