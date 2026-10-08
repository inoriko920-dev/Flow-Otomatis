"""R04 static linkage gate for ASTRA's explicit T01–T25 regression matrix.

This test ensures every audit case remains linked to a pytest function. The
full CI quality job also *executes* all unit/contract/integration/smoke/UI
tests; this inventory by itself is not behavioral evidence.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_CASES: tuple[tuple[str, str, str], ...] = (
    (
        "T01",
        "tests/integration/test_gemini_keys_foundation.py",
        "test_t01_t02_health_completion_never_changes_newer_manual_selection",
    ),
    (
        "T02",
        "tests/integration/test_gemini_keys_foundation.py",
        "test_t01_t02_health_completion_never_changes_newer_manual_selection",
    ),
    (
        "T03",
        "tests/integration/test_gemini_keys_foundation.py",
        "test_t03_deleted_key_is_not_resurrected_by_health_completion",
    ),
    (
        "T04",
        "tests/integration/test_gemini_keys_foundation.py",
        "test_t04_late_old_health_result_cannot_replace_newer_completion",
    ),
    (
        "T05",
        "tests/ui/test_gemini_agent_workspace.py",
        "test_t05_t06_stale_agent_completion_cannot_replace_next_scene_or_unlock_busy",
    ),
    (
        "T06",
        "tests/ui/test_gemini_agent_workspace.py",
        "test_t05_t06_stale_agent_completion_cannot_replace_next_scene_or_unlock_busy",
    ),
    (
        "T07",
        "tests/ui/test_gemini_agent_workspace.py",
        "test_t07_same_scene_id_in_other_project_does_not_receive_old_answer",
    ),
    (
        "T08",
        "tests/ui/test_gemini_agent_workspace.py",
        "test_t08_close_window_during_agent_request_does_not_touch_destroyed_receiver",
    ),
    (
        "T09",
        "tests/integration/test_local_generation_queue_wave.py",
        "test_t09_folder_image_deleted_after_prepare_blocks_submit",
    ),
    (
        "T10",
        "tests/integration/test_local_generation_queue_wave.py",
        "test_t10_zip_source_unavailable_blocks_provider",
    ),
    (
        "T11",
        "tests/integration/test_local_generation_queue_wave.py",
        "test_t11_modified_image_bytes_same_name_blocks_and_reprepare_works",
    ),
    (
        "T12",
        "tests/integration/test_local_generation_queue_wave.py",
        "test_t12_unreadable_image_maps_to_pre_submit_attention",
    ),
    (
        "T13",
        "tests/integration/test_local_generation_queue_wave.py",
        "test_t13_verified_zip_image_submits_once_and_ambiguity_is_not_retried",
    ),
    (
        "T14",
        "tests/integration/test_local_results_wave.py",
        "test_t14_missing_video_is_effectively_unavailable_without_erasing_history",
    ),
    (
        "T15",
        "tests/integration/test_local_results_wave.py",
        "test_t15_effective_download_requires_readable_nonempty_regular_file",
    ),
    (
        "T16",
        "tests/integration/test_local_results_wave.py",
        "test_t16_manifest_checks_availability_after_snapshot_and_before_export",
    ),
    (
        "T17",
        "tests/ui/test_real_results_view.py",
        "test_t17_missing_video_displays_unavailable_and_blocks_export",
    ),
    (
        "T18",
        "tests/integration/test_generated_media_download_foundation.py",
        "test_t18_collision_appearing_during_download_never_overwrites_final",
    ),
    (
        "T19",
        "tests/integration/test_generated_media_download_foundation.py",
        "test_t19_unsupported_no_clobber_primitive_fails_without_fallback",
    ),
    (
        "T20",
        "tests/integration/test_generated_media_download_foundation.py",
        "test_t20_parallel_attempts_publish_once_and_do_not_erase_success",
    ),
    (
        "T21",
        "tests/integration/test_generated_media_download_foundation.py",
        "test_t21_file_publish_success_db_failure_requires_manual_reconciliation",
    ),
    (
        "T22",
        "tests/integration/test_project_library_wave.py",
        "test_t22_t23_naive_empty_and_invalid_timestamps_are_isolated_read_only",
    ),
    (
        "T23",
        "tests/integration/test_project_library_wave.py",
        "test_t22_t23_naive_empty_and_invalid_timestamps_are_isolated_read_only",
    ),
    (
        "T24",
        "tests/integration/test_project_library_wave.py",
        "test_t24_offsets_sort_by_absolute_instant_not_wall_clock",
    ),
    (
        "T25",
        "tests/integration/test_project_library_wave.py",
        "test_t25_naive_load_and_scan_preserve_db_byte_checksum",
    ),
)


def test_r04_case_matrix_is_complete_and_nonduplicated() -> None:
    """R01 through R03 regression IDs must cover T01 through T25 exactly once."""

    expected = {f"T{index:02d}" for index in range(1, 26)}
    actual = [case_id for case_id, _path, _function in _CASES]
    assert len(actual) == len(expected)
    assert set(actual) == expected


@pytest.mark.parametrize(
    ("case_id", "relative_path", "function"), _CASES, ids=[c[0] for c in _CASES]
)
def test_r04_case_maps_to_real_pytest_function(
    case_id: str,
    relative_path: str,
    function: str,
) -> None:
    """Reject silent renames or deletion of an ASTRA acceptance test."""

    path = _ROOT / relative_path
    assert path.is_file(), f"{case_id}: test module missing: {relative_path}"
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names = {
        node.name
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }
    assert function in names, f"{case_id}: {relative_path} is missing {function}"


def test_r04_ci_executes_all_five_suites_and_windows_gates() -> None:
    """Inventory tests and real behavioral tests run in the same workflow."""

    workflow = (_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for required in (
        "tests/unit",
        "tests/contract",
        "tests/integration",
        "tests/smoke",
        "tests/ui",
        "capture_ui_reference_suite.py",
        "compare_ui_references.py",
        "stage_browsers.py",
        "smoke_browser_runtime.py",
        "build_portable.py",
        "smoke_portable.py",
    ):
        assert required in workflow, f"R04 gate missing from CI: {required}"
