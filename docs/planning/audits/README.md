# STEP 12 Audit Remediation Index — 7 October 2026

## Authority
Primary audit document:
- `00_ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-07.docx`
- original uploaded source SHA-256: `1011693e1e67673a4af49378ca2009e93f596a74f563276ae060ebcaae0ca210` (48486 bytes)
- repository compact text-equivalent SHA-256: `39ee9d8c37aa573f019649b7f6f04c76812e80cf88b397e5694e0c96f9946527` (10028 bytes)
- repository-copy verification: complete logical audit text preserved in order; DOCX opened and rendered cleanly to five pages; original visual layout was intentionally simplified after the first binary upload was detected as truncated.
- ASTRA baseline: `e6724a0a5c3d68789149ed5c7eb094d44c9f0967`

This audit is a remediation track inside STEP 12. It does not restart Software Factory planning and does not replace the frozen UI reference.

## Findings still applicable at A00 start
- F01 P1 — missing prompt TXT can be treated as READY.
- F02 P1 — duplicate import can retain stale generation/download data.
- F03 P1 before live — queued request can mix stale duration with newer scene state.
- F04 P2 — corrupt scene row can break project listing.
- F05 P1 — Google session probing runs synchronously on the Qt UI thread.
- F06 P2 before live — orphan RUNNING jobs have no real recovery transition.

No production fix is included in A00.

## Package order
- A00 — source-of-truth synchronization and baseline verification.
- A01 — F01 + F02 import/data linkage.
- A02 — F04 corrupt-data isolation.
- A03 — F03 + F06 queue revision/lease/recovery.
- A04 — F05 browser worker ownership and UI responsiveness.
- A05 — combined verification/build/handoff.

Each package is executed separately. Do not skip ahead. Live Flow generation remains blocked by the pre-existing real-account gate.

## A00 documentation decisions
A00 records the cross-layer decisions needed before implementation:
- ADR-015 — atomic workspace create vs update semantics for A01.
- ADR-016 — generation request revision/fingerprint plus owner/lease recovery for A03.
- ADR-017 — Browser Worker ownership and async UI command boundary for A04.

## Current A00 state
A00: **PASS**.

Evidence:
- documentation-sync commit: `bc550e57407d1be09fceb64eadd18217f4d9c37c`;
- official CI run: `37639865121`;
- quality job: `112855631708` — SUCCESS;
- CPython 3.14.7 x64;
- uv 0.12.23;
- frozen sync PASS;
- Ruff format/lint PASS;
- mypy PASS — 63 source files;
- architecture guard PASS;
- pytest PASS — 90 passed.

The next package is A01 only. Live Generate remains BLOCKED.

## Current A01 state
A01: **PASS**.

Closed:
- F01 — a missing prompt TXT reference is no longer accepted as literal usable prompt text.
- F02 — a second import/create for an existing episode no longer replaces Scene content while retaining old results.

Implementation:
- merge SHA: `865e92f4a3da01a35339203f263ab938a420d3bd`;
- PR #1 head: `2aa9de28ce0ba379d3ed11b1ba1d6a035d5b01a4`;
- explicit repository `create` / `update` semantics;
- atomic duplicate detection with SQLite `BEGIN IMMEDIATE`;
- typed `WorkspaceAlreadyExistsError`;
- typed `PROMPT_FILE_MISSING` for ZIP and folder package readers;
- safe Indonesian UI handling;
- real generation-job/download repositories used in regression coverage.

Official main evidence:
- CI run: `37644208386` — SUCCESS;
- quality: `112870617392` — SUCCESS;
- UI visual: `112871584570` — SUCCESS;
- package Windows: `112872148801` — SUCCESS;
- pytest: 95 passed;
- mypy: 63 source files, no issues;
- architecture guard: PASS;
- UI: 30/30 PASS, similarity 0.6344–0.9643;
- Playwright Chromium smoke: PASS;
- portable smoke: PASS;
- UI artifact: `11493692056`, SHA-256 `b0e8d1671e0e368b21a09a31595e9502efd9e0efe8e6ce61db89539bc645a200`;
- Windows artifact: `11494735790`, 435479977 bytes, SHA-256 `8a17a7f24aaa203877326952fe97f3b711c40ceac3a603fd3310b76b5c0990a9`.

Evidence file:
- `A01_IMPORT_INTEGRITY_EVIDENCE_2026-10-07.md`

Next package is A02 only: isolate F04 corrupt project data. F03/F05/F06 remain open. Live Generate remains BLOCKED.

