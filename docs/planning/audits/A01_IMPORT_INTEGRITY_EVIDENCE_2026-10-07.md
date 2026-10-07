# A01 Import Integrity Evidence — 7 October 2026

## Scope
STEP 12 audit-remediation package A01 only.

Findings:
- F01 — missing prompt TXT accepted as literal prompt text.
- F02 — duplicate import replaced Scene content while prior generation/download results survived.

A02/F04, A03/F03+F06, and A04/F05 were not implemented in this package.

## Implementation identity
- Base after A00: `5de0472349e17a9bd353825c190503430482d7de`
- Work branch: `sol/a01-import-integrity`
- PR head: `2aa9de28ce0ba379d3ed11b1ba1d6a035d5b01a4`
- PR: #1
- Main merge SHA: `865e92f4a3da01a35339203f263ab938a420d3bd`

The base-to-merge diff contains exactly eight implementation/test files:
- `application/ports/workspace_repository.py`
- `application/services/episode_import.py`
- `application/services/scene_planning.py`
- `domain/errors.py`
- `infrastructure/filesystem/episode_package_reader.py`
- `infrastructure/persistence/sqlite_workspace_repository.py`
- `presentation/main_window.py`
- `tests/integration/test_episode_import_slice.py`

## F01 closure
- a one-line package prompt value ending in `.txt` remains a file-reference contract;
- ZIP and folder paths both raise `PackageValidationError` with code `PROMPT_FILE_MISSING` when the file is absent;
- validation stops before workspace creation;
- error text includes Scene ID plus the safe relative reference;
- empty referenced text resolves to an empty prompt and is not READY;
- valid UTF-8 prompt text is loaded;
- existing package path-security validation remains active.

## F02 closure
- new workspace import uses `WorkspaceRepositoryPort.create`;
- Scene planning uses `WorkspaceRepositoryPort.update`;
- SQLite create obtains `BEGIN IMMEDIATE` and rejects an existing project row with typed `WorkspaceAlreadyExistsError`;
- duplicate create never uses destructive replace/merge semantics;
- prior generation jobs and download results are preserved;
- concurrent create regression proves one creator succeeds and the other is rejected;
- Qt create action catches the typed duplicate and shows an Indonesian action message pointing to the existing project.

## Pre-push local diagnostic
A focused synthetic SQLite validation was executed before the connector write recovered:
- 4 focused scenarios passed;
- missing prompt failed before DB creation;
- UTF-8/empty prompt behavior passed;
- duplicate import preserved real SQLite job/download records;
- concurrent create produced one create + one duplicate.

This local diagnostic is supplemental; official Windows CI below is authoritative.

## Official PR CI
Run `37643429473`: SUCCESS.
- quality `112867913827`: SUCCESS;
- UI visual `112868654601`: SUCCESS;
- package Windows `112869045702`: SUCCESS;
- pytest: 95 passed;
- frozen UI: 30/30 PASS;
- portable smoke: PASS.

## Official main CI
Run `37644208386`: SUCCESS.

Quality job `112870617392`:
- CPython 3.14.7 x64;
- uv 0.12.23;
- Ruff format PASS — 125 files already formatted;
- Ruff lint PASS;
- mypy PASS — no issues in 63 source files;
- architecture guard PASS;
- pytest PASS — 95 passed, 1827 warnings.

UI visual job `112871584570`:
- 30/30 fixtures PASS;
- similarity range 0.6344–0.9643;
- artifact ID `11493692056`;
- artifact SHA-256 `b0e8d1671e0e368b21a09a31595e9502efd9e0efe8e6ce61db89539bc645a200`;
- artifact size 3316911 bytes.

Package job `112872148801`:
- staged Playwright Chromium smoke PASS;
- PyInstaller onedir/portable ZIP build PASS;
- portable application smoke PASS;
- artifact ID `11494735790`;
- artifact size 435479977 bytes;
- artifact SHA-256 `8a17a7f24aaa203877326952fe97f3b711c40ceac3a603fd3310b76b5c0990a9`.

## Gate
A01: **PASS**.

Acceptance result:
- F01 closed;
- F02 closed;
- failed missing-prompt import creates no workspace;
- duplicate import changes no existing project/jobs/download results;
- old duration and ZIP traversal regressions remain green in the full suite;
- frozen UI contract remains green;
- Windows portable build remains green.

Live Google Flow generation remains blocked by the pre-existing real-account restart validation.
