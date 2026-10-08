# STEP 12 — SOL R04 Combined Acceptance Matrix
Date: 8 October 2026 WIB
Stage: R04 COMPLETE / OFFICIAL MAIN CI PASS
Repo: `inoriko920-dev/Flow-Otomatis`
Base main SHA: `c23f00383438f95021514e5e24ef496e618e20c7`
Authority: `ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-08.docx`, ADR-016/018/019, R01–R03 evidence.

## Intent
This R04 changes no production feature and no frozen UI. A small contract test maps **T01–T25** to the already implemented test owners; official quality runs all suites (not just inventory). Pass requires full official fresh CI on one combined tree, real Windows UI reference 30-state comparison and portable Chromium/build/smoke. Artifact SHA/digest and source SHA will be recorded only after the run completes.

## B01–B06 acceptance map
| ID | Finding | Canonical pytest function | Coverage |
|---|---|---|---|
| T01 | B01 | `test_t01_t02_health_completion_never_changes_newer_manual_selection` | Gemini manual selection after health A |
| T02 | B01 | `test_t01_t02_health_completion_never_changes_newer_manual_selection` | Gemini manual selection after health B |
| T03 | B01 | `test_t03_deleted_key_is_not_resurrected_by_health_completion` | Deleted key is not resurrected |
| T04 | B01 | `test_t04_late_old_health_result_cannot_replace_newer_completion` | Late health cannot override newer |
| T05 | B02 | `test_t05_t06_stale_agent_completion_cannot_replace_next_scene_or_unlock_busy` | Stale success/error isolation |
| T06 | B02 | `test_t05_t06_stale_agent_completion_cannot_replace_next_scene_or_unlock_busy` | Current request busy state remains true |
| T07 | B02 | `test_t07_same_scene_id_in_other_project_does_not_receive_old_answer` | Different episode same Scene ID isolation |
| T08 | B02 | `test_t08_close_window_during_agent_request_does_not_touch_destroyed_receiver` | Agent signal receiver close lifecycle |
| T09 | B03 | `test_t09_folder_image_deleted_after_prepare_blocks_submit` | Missing folder image pre-submit |
| T10 | B03 | `test_t10_zip_source_unavailable_blocks_provider` | ZIP image/source removed |
| T11 | B03 | `test_t11_modified_image_bytes_same_name_blocks_and_reprepare_works` | Same-path image content changed |
| T12 | B03 | `test_t12_unreadable_image_maps_to_pre_submit_attention` | Unreadable image prevents submit |
| T13 | B03 | `test_t13_verified_zip_image_submits_once_and_ambiguity_is_not_retried` | One verified ZIP submit, ambiguity no retry |
| T14 | B04 | `test_t14_missing_video_is_effectively_unavailable_without_erasing_history` | Missing output preserves history |
| T15 | B04 | `test_t15_effective_download_requires_readable_nonempty_regular_file` | Nonempty/readable regular output |
| T16 | B04 | `test_t16_manifest_checks_availability_after_snapshot_and_before_export` | Independent pre-export recheck |
| T17 | B04 | `test_t17_missing_video_displays_unavailable_and_blocks_export` | Qt Hasil status and no handoff |
| T18 | B05 | `test_t18_collision_appearing_during_download_never_overwrites_final` | Destination race does not clobber |
| T19 | B05 | `test_t19_unsupported_no_clobber_primitive_fails_without_fallback` | Unsupported hardlink fails safely |
| T20 | B05 | `test_t20_parallel_attempts_publish_once_and_do_not_erase_success` | Concurrent download winners/losers |
| T21 | B05 | `test_t21_file_publish_success_db_failure_requires_manual_reconciliation` | Published file with DB failure |
| T22 | B06 | `test_t22_t23_naive_empty_and_invalid_timestamps_are_isolated_read_only` | Timezone-naive project isolation |
| T23 | B06 | `test_t22_t23_naive_empty_and_invalid_timestamps_are_isolated_read_only` | Malformed timestamp isolation |
| T24 | B06 | `test_t24_offsets_sort_by_absolute_instant_not_wall_clock` | Mixed timezone ordering |
| T25 | B06 | `test_t25_naive_load_and_scan_preserve_db_byte_checksum` | Corruption read is non-mutating |

## Parallel safeguards from earlier CI
- Non-numbered tests: read-only Gemini Agent & keyring masking, stale request fingerprints and ambiguous no-retry, Qt heartbeat, ZIP path safety, manifest v1.0 compatibility, conditional SQLite concurrent failures, frozen Hasil and Project Hub recoverability.
- False confidence boundary: static inventory does not itself execute 25 behavior cases. Full workflow `ci.yml` runs all tests in unit/contract/integration/smoke/ui in addition to this matrix.
- R04 must not claim real Google key health or real Google Flow login, Generate, Download, browser selectors, or user-machine conditions are verified.
- Original standalone ASTRA reproduction scripts were not provided; test references are direct repository regression tests, not a recreated original harness.
- Manifest v1.0 `UNAVAILABLE` has not been certified against external strict-enum consumers. R04 does not silently change that contract.

## CI gating checklist — verified from exact merged-main R04 run
- [x] inventory T01–T25 mapped and executed by the official test suite
- [x] frozen dependency sync, Ruff format/lint, mypy and architecture PASS
- [x] pytest full suite PASS and actual number recorded
- [x] 30 actual UI compositions compared to frozen reference PASS
- [x] Windows staged Chromium smoke, portable build and executable smoke PASS
- [x] artifact IDs, SHA-256, size, expiration, source SHA recorded
- [x] docs/handoff and project status updated; stop before any live Google workflow

Official checked `main` SHA: `baf3257b293f6b05b4cdbca7e9f3d4aa1272d218`; full CI run `37725495137`, SUCCESS all 3 jobs. Pytest 192 passed, frozen UI 30/30 PASS, Windows Chromium/portable build/smoke PASS; artifact SHA and retention are recorded in `B01_B06_R04_FINAL_EVIDENCE_2026-10-08.md`. Later evidence-only commit is not a new source-code test run.
