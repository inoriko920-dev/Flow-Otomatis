"""Pure offline simulation engine for explicit synthetic profile budgets.

Never accesses real Google accounts, provider balances or browser automation.
"""

from __future__ import annotations

import re
from typing import Any

_SUPPORTED_DURATIONS = (4, 6, 8, 10)
_OPAQUE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
_MAX_CREDITS = 1_000_000_000


class InvalidSimulationInput(ValueError):
    """Invalid or unsafe fake-only plan input."""


def _exact_keys(value: object, required: set[str], *, where: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != required:
        raise InvalidSimulationInput(f"{where}: expected only keys {sorted(required)}")
    if not all(isinstance(key, str) for key in value):
        raise InvalidSimulationInput(f"{where}: keys must be strings")
    return value


def _credit(value: object, *, where: str, allow_zero: bool = True) -> int:
    if type(value) is not int or value < (0 if allow_zero else 1) or value > _MAX_CREDITS:
        raise InvalidSimulationInput(
            f"{where}: expected a whole number between {0 if allow_zero else 1} and {_MAX_CREDITS}"
        )
    return value


def _identifier(value: object, *, where: str) -> str:
    if not isinstance(value, str) or not _OPAQUE_ID.fullmatch(value):
        raise InvalidSimulationInput(
            f"{where}: use a non-secret opaque ID (letters, numbers, _ or -)"
        )
    return value


def simulate(payload: object) -> dict[str, Any]:
    """Return deterministic fake-only assignments; never dispatch any work.

    No stored credits or rates are trusted as real. Every call is isolated;
    two projects must appear in the same input to share one simulated budget.
    """

    source = _exact_keys(
        payload,
        {"mode", "profiles", "scenes", "rates_per_video", "max_total_credits"},
        where="plan",
    )
    if source["mode"] != "OFFLINE_SIMULATION":
        raise InvalidSimulationInput("mode must be exactly OFFLINE_SIMULATION")

    raw_profiles = source["profiles"]
    raw_scenes = source["scenes"]
    if not isinstance(raw_profiles, list) or not 1 <= len(raw_profiles) <= 100:
        raise InvalidSimulationInput("profiles must contain 1 to 100 synthetic profiles")
    if not isinstance(raw_scenes, list) or not 1 <= len(raw_scenes) <= 10_000:
        raise InvalidSimulationInput("scenes must contain 1 to 10000 scenes")

    rates = _exact_keys(
        source["rates_per_video"],
        {"4", "6", "8", "10"},
        where="rates_per_video",
    )
    costs = {
        seconds: _credit(rates[str(seconds)], where=f"rate {seconds}", allow_zero=False)
        for seconds in _SUPPORTED_DURATIONS
    }
    total_ceiling = _credit(source["max_total_credits"], where="max_total_credits")

    remaining: dict[str, int] = {}
    used: dict[str, int] = {}
    profile_ceiling: dict[str, int] = {}
    for index, raw in enumerate(raw_profiles):
        item = _exact_keys(
            raw,
            {"profile_id", "simulated_balance", "max_spend"},
            where=f"profiles[{index}]",
        )
        key = _identifier(item["profile_id"], where=f"profiles[{index}].profile_id")
        if key in remaining:
            raise InvalidSimulationInput(f"Duplicate profile ID: {key}")
        balance = _credit(item["simulated_balance"], where=f"profiles[{index}].simulated_balance")
        limit = _credit(item["max_spend"], where=f"profiles[{index}].max_spend")
        remaining[key] = balance
        profile_ceiling[key] = min(limit, balance)
        used[key] = 0

    assignments: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    total_used = 0
    for index, raw in enumerate(raw_scenes):
        item = _exact_keys(
            raw, {"project_id", "scene_id", "duration_s", "outputs"}, where=f"scenes[{index}]"
        )
        project_id = _identifier(item["project_id"], where=f"scenes[{index}].project_id")
        scene_id = _identifier(item["scene_id"], where=f"scenes[{index}].scene_id")
        key = (project_id, scene_id)
        if key in seen:
            raise InvalidSimulationInput(f"Duplicate work: {project_id}/{scene_id}")
        seen.add(key)
        seconds = item["duration_s"]
        if type(seconds) is not int or seconds not in _SUPPORTED_DURATIONS:
            raise InvalidSimulationInput("duration_s must be exactly 4, 6, 8 or 10")
        outputs = _credit(item["outputs"], where=f"scenes[{index}].outputs", allow_zero=False)
        if outputs > 8:
            raise InvalidSimulationInput("outputs must be between 1 and 8")
        quoted_cost = costs[seconds] * outputs
        common = {
            "project_id": project_id,
            "scene_id": scene_id,
            "duration_s": seconds,
            "outputs": outputs,
            "simulated_cost": quoted_cost,
        }

        if total_used + quoted_cost > total_ceiling:
            blocked.append({**common, "reason": "SIMULATED_TOTAL_BUDGET_EXCEEDED"})
            continue

        eligible = [
            profile_id
            for profile_id in remaining
            if remaining[profile_id] >= quoted_cost
            and used[profile_id] + quoted_cost <= profile_ceiling[profile_id]
        ]
        if not eligible:
            blocked.append({**common, "reason": "SIMULATED_PROFILE_BUDGET_EXCEEDED"})
            continue

        # Balance high-water first, stable opaque ID as a deterministic tie-breaker.
        selected = min(
            eligible,
            key=lambda profile_id: (
                -min(remaining[profile_id], profile_ceiling[profile_id] - used[profile_id]),
                profile_id,
            ),
        )
        remaining[selected] -= quoted_cost
        used[selected] += quoted_cost
        total_used += quoted_cost
        assignments.append({**common, "profile_id": selected})

    return {
        "mode": "OFFLINE_SIMULATION",
        "live_dispatch_allowed": False,
        "provider_evidence": "NONE",
        "warning": (
            "Synthetic balances and user-entered tariffs are NOT verified Google Flow "
            "credits, eligibility, provider permission, or authorization to generate."
        ),
        "total_simulated_credits": total_used,
        "max_total_simulated_credits": total_ceiling,
        "assigned": assignments,
        "blocked": blocked,
        "profiles": [
            {
                "profile_id": profile_id,
                "used_simulated_credits": used[profile_id],
                "remaining_simulated_balance": remaining[profile_id],
            }
            for profile_id in sorted(remaining)
        ],
    }
