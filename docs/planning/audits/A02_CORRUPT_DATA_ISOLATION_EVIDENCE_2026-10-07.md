# A02 Corrupt Data Isolation Evidence — 7 October 2026

## Scope
STEP 12 audit-remediation package A02 only.

Finding closed:
- F04 — one corrupt persisted Scene/project could throw an unwrapped decode error and break project listing.

A03/F03+F06 and A04/F05 were not implemented here.

## Implementation identity
- A01 documentation baseline: `e6eec8dd29cccee7ffa9575cce14cd8d983860c7`
- Work branch: `sol/a02-corrupt-data-isolation`
- Initial implementation: `c5bf5ab10bac249dfdfc54ca70a909510ce0af8b`
- Formatting correction: `989a57dc026f9544334803711c99544caad1044e`
- PR: #2
- Main merge SHA: `9525a9d8ed370ab8b3f3ed916735e03ef04ecfce`

The baseline-to-merge diff contains exactly eight files:
- `application/ports/workspace_repository.py`
- `application/services/project_library.py`
- `domain/errors.py`
- `infrastructure/persistence/sqlite_workspace_repository.py`
- `presentation/main_window.py`
- `presentation/project_hub_view.py`
- `tests/integration/test_project_library_wave.py`
- `tests/ui/test_project_hub_recovery.py`

## F04 closure
- canonical workspace load uses SQLite URI `mode=ro`;
- read path does not run schema creation/repair;
- invalid enum, numeric, timestamp, episode identity, and database decoding failures are normalized to typed storage/corrupt-data errors;
- resilient library scan separates healthy workspaces from `CORRUPT` and `UNAVAILABLE` entries;
- healthy projects remain listable/openable when another project is corrupt;
- Project Hub shows corrupt/unavailable rows honestly inside the existing frozen layout;
- Qt open callbacks catch typed failures and show safe Indonesian actions;
- corrupt source database is not deleted, modified, or silently repaired.

## Regression proof
Integration tests include:
- healthy + `INVALID_ENUM` project in the same library;
- direct load/open of corrupt project raises typed `WorkspaceCorruptError`;
- invalid `imported_at` timestamp;
- invalid numeric `target_duration_s`;
- healthy project remains openable;
- corrupt DB SHA-256 remains identical before and after listing/open attempts.

UI regression includes:
- healthy and corrupt entries shown together;
- corrupt entry displays `Data Rusak`;
- opening corrupt row stays on Project Hub and produces a safe warning;
- warning says the project file was not changed;
- healthy row remains openable afterward.

## CI history
First PR CI `37646442531` failed only the Ruff format check for three files before test execution. No product failure was observed. Formatting was corrected in `989a57dc...`.

Second PR CI `37646690567`: SUCCESS.
- quality `112879193063`: SUCCESS — 99 passed;
- UI visual `112879689212`: SUCCESS — 30/30;
- package Windows `112880303671`: SUCCESS — Chromium smoke and portable smoke PASS.

## Official main CI
Run `37647427626`: SUCCESS.

Quality `112881739521`:
- Ruff format PASS — 127 files already formatted;
- Ruff lint PASS;
- mypy PASS — no issues in 63 source files;
- architecture guard PASS;
- pytest PASS — 99 passed, 1904 warnings.

UI visual `112882633481`:
- 30/30 fixtures PASS;
- similarity 0.6344–0.9643;
- artifact ID `11494409352`;
- size 3316911 bytes;
- SHA-256 `3a213c84085d22340b5bdc7f0bd8882ffeeff6becf5c8416ecef0c06fb01c20f`.

Package `112883036794`:
- staged Playwright Chromium smoke PASS;
- portable ZIP build PASS;
- portable application smoke PASS;
- artifact ID `11495321054`;
- size 435481873 bytes;
- SHA-256 `fa9bd2be4725cc1af42d84b09755d2ca5f3f1862125c7cef98ab847d2684181e`.

## Gate
A02: **PASS**.

F04 is closed. Live Google Flow generation remains blocked by the independent real-account restart-validation gate.
