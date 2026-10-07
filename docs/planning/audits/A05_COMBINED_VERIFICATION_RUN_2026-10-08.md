# A05 Combined Verification Run — 8 October 2026

Status: IN PROGRESS

This file starts the final STEP 12 audit-remediation verification package A05. No production feature change is included.

## Acceptance matrix mapping
- T01 — missing prompt TXT ZIP/folder: `test_missing_prompt_txt_reference_is_rejected_for_zip_before_persistence`, `test_missing_prompt_txt_reference_is_rejected_for_folder`.
- T02 — valid/empty/inline/traversal prompt behavior: `test_prompt_txt_empty_is_not_ready_and_valid_utf8_is_loaded`, existing happy-path inline prompt coverage, and `test_zip_path_traversal_is_rejected`.
- T03 — duplicate import atomicity/data preservation: `test_duplicate_import_is_rejected_without_changing_workspace_jobs_or_downloads`, `test_atomic_create_allows_only_one_concurrent_creator`.
- T04 — edit after enqueue: `test_edit_after_enqueue_blocks_provider_until_explicit_reprepare`.
- T05 — image loss after enqueue: `test_image_missing_after_enqueue_blocks_provider_without_mixing_revision`.
- T06 — healthy project beside corrupt data: `test_corrupt_project_is_isolated_and_read_does_not_mutate_source` plus invalid persisted-type coverage.
- T07 — slow driver + duplicate command: `test_slow_session_probe_keeps_qt_heartbeat_responsive`, `test_browser_commands_use_one_owner_and_reject_same_profile_duplicate`.
- T08 — bounded close/shutdown while active: `test_browser_command_shutdown_wait_is_bounded_during_slow_probe`.
- T09 — reopen/orphan recovery with zero blind submit: `test_expired_orphan_before_and_after_submit_boundary_are_distinguished`.
- T10 — second owner cannot steal active work: `test_active_owner_lease_cannot_be_stolen_by_second_instance`.
- T11 — migration preservation + atomic rollback: `test_migration_preserves_generated_result_and_existing_download`, `test_failed_schema_migration_rolls_back_all_added_columns`.
- T12 — fresh official runtime, complete regression, visual regression, Windows package and portable smoke: supplied by the CI run triggered by this commit.

## Required interpretation
A05 PASS will verify the local audit remediation track only. It does not prove real Google-account login/restart persistence and does not authorize I12-02B2-LIVE.
