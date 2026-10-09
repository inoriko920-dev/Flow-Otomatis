"""Offline coordinator prototype tests: synthetic profiles only, zero provider calls."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.offline_credit_simulator import InvalidSimulationInput, main, simulate


def _input() -> dict:
    return {
        "mode": "OFFLINE_SIMULATION",
        "profiles": [
            {"profile_id": "fake-A", "simulated_balance": 20, "max_spend": 20},
            {"profile_id": "fake-B", "simulated_balance": 20, "max_spend": 20},
        ],
        "scenes": [
            {"project_id": "project-one", "scene_id": "SCENE_001", "duration_s": 10, "outputs": 1},
            {"project_id": "project-two", "scene_id": "SCENE_001", "duration_s": 10, "outputs": 1},
            {"project_id": "project-one", "scene_id": "SCENE_002", "duration_s": 10, "outputs": 1},
        ],
        "rates_per_video": {"4": 7, "6": 10, "8": 12, "10": 15},
        "max_total_credits": 100,
    }


def test_two_projects_share_one_global_simulated_profile_budget() -> None:
    result = simulate(_input())
    assert result["live_dispatch_allowed"] is False
    assert result["provider_evidence"] == "NONE"
    assert [item["profile_id"] for item in result["assigned"]] == ["fake-A", "fake-B"]
    assert result["total_simulated_credits"] == 30
    assert len(result["blocked"]) == 1
    assert result["blocked"][0]["reason"] == "SIMULATED_PROFILE_BUDGET_EXCEEDED"
    assert {row["used_simulated_credits"] for row in result["profiles"]} == {15}
    assert result == simulate(_input())


def test_total_budget_never_exceeded_even_with_sufficient_profiles() -> None:
    data = _input()
    data["max_total_credits"] = 25
    report = simulate(data)
    assert report["total_simulated_credits"] == 15
    assert len(report["assigned"]) == 1
    assert len(report["blocked"]) == 2
    assert all(
        item["reason"] == "SIMULATED_TOTAL_BUDGET_EXCEEDED" for item in report["blocked"]
    )


def test_per_profile_limit_is_stricter_than_simulated_balance() -> None:
    data = _input()
    data["profiles"][0]["max_spend"] = 0
    report = simulate(data)
    assert len(report["assigned"]) == 1
    assert report["assigned"][0]["profile_id"] == "fake-B"
    assert report["profiles"][0]["remaining_simulated_balance"] == 20


def test_4_6_8_10_costs_multiply_by_outputs_not_only_scene_count() -> None:
    data = _input()
    data["profiles"] = [{"profile_id": "fake-A", "simulated_balance": 200, "max_spend": 200}]
    data["scenes"] = [
        {
            "project_id": "proj",
            "scene_id": f"SCENE_{index:03}",
            "duration_s": seconds,
            "outputs": 2,
        }
        for index, seconds in enumerate((4, 6, 8, 10), start=1)
    ]
    report = simulate(data)
    assert [row["simulated_cost"] for row in report["assigned"]] == [14, 20, 24, 30]
    assert report["total_simulated_credits"] == 88


@pytest.mark.parametrize(
    ("path", "bad_value"),
    [
        (("mode",), "LIVE"),
        (("profiles", 0, "profile_id"), "somebody@example.com"),
        (("profiles", 0, "simulated_balance"), True),
        (("profiles", 0, "max_spend"), -1),
        (("scenes", 0, "duration_s"), 7),
        (("scenes", 0, "duration_s"), 8.0),
        (("scenes", 0, "outputs"), 0),
        (("scenes", 0, "outputs"), 100),
        (("rates_per_video", "4"), 0),
        (("max_total_credits",), False),
    ],
)
def test_invalid_input_fails_closed(path: tuple, bad_value: object) -> None:
    data = _input()
    cursor = data
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = bad_value
    with pytest.raises(InvalidSimulationInput):
        simulate(data)


def test_duplicate_scene_or_profile_denied() -> None:
    data = _input()
    data["profiles"][1]["profile_id"] = "fake-A"
    with pytest.raises(InvalidSimulationInput, match="Duplicate profile"):
        simulate(data)

    data = _input()
    data["scenes"][1] = deepcopy(data["scenes"][0])
    with pytest.raises(InvalidSimulationInput, match="Duplicate work"):
        simulate(data)


def test_rejects_extra_sensitive_fields_and_unknown_rates() -> None:
    data = _input()
    data["profiles"][0]["cookie"] = "never copy real cookies"
    with pytest.raises(InvalidSimulationInput):
        simulate(data)

    data = _input()
    data["rates_per_video"]["12"] = 20
    with pytest.raises(InvalidSimulationInput):
        simulate(data)


def test_cli_writes_new_report_without_overwriting(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "report.json"
    input_path.write_text(json.dumps(_input()), encoding="utf-8")

    assert main([str(input_path), "--output", str(output_path)]) == 0
    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["mode"] == "OFFLINE_SIMULATION"
    assert saved["total_simulated_credits"] == 30

    with pytest.raises(SystemExit) as error:
        main([str(input_path), "--output", str(output_path)])
    assert error.value.code == 2
    assert json.loads(output_path.read_text(encoding="utf-8")) == saved

    assert main([str(input_path)]) == 0
    assert json.loads(capsys.readouterr().out) == saved
