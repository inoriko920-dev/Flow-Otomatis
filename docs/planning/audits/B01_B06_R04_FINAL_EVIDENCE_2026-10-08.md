# STEP 12 — SOL R04 Combined Audit FINAL EVIDENCE
**Date:** 8 October 2026 WIB
**Scope:** `inoriko920-dev/Flow-Otomatis`, ASTRA 8 October findings B01–B06, **OFFLINE/Windows CI**.
**Outcome:** **R04 PASS / COMPLETE**, no production feature change during R04.

## Authoritative scope and source
- ASTRA original DOCX: `docs/planning/audits/ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-08.docx`, SHA-256 `5481a09b85219615169c285d6bfd42bcc7398bcf881a73a604f2e7a351444fda`; original standalone ASTRA reproduction .py/.json were not supplied.
- ADR-016 (image hash prepared revision), ADR-018 (B01–B06 requirements), ADR-019 (download availability and no-clobber).
- R01 B01/B02: PR #14 and CI `37721917858` SUCCESS, 137 tests; R02 B03/B06: PR #15 and CI `37723155562` SUCCESS, 153 tests; R03 B04/B05: PR #16 and CI `37724196252` SUCCESS, 165 tests.
- R04 PR #17: https://github.com/inoriko920-dev/Flow-Otomatis/pull/17. Scope diff against prior main: **two added files only**, `tests/contract/test_step12_r04_acceptance_matrix.py` and `docs/planning/audits/STEP12_R04_COMBINED_ACCEPTANCE_MATRIX_2026-10-08.md`; no application source or frozen UI file modifications.
- R04 PR tested SHA `e557a2219350871205d32330c3a0d027bb9e9824` and PR CI https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37725045658 (SUCCESS).
- Squash-merged production/tests tree SHA `baf3257b293f6b05b4cdbca7e9f3d4aa1272d218`; **fresh main push CI** https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37725495137 (SUCCESS, all 3 jobs). The later status/evidence/handoff commit is documentation-only and does not change tested source.

## Combined audit matrix
- T01–T04: B01 Gemini key manual selection, deletion and race ordering.
- T05–T08: B02 Qt Agent stale answers/errors, workspace/Scene revision, close lifetime.
- T09–T13: B03 ZIP/folder approved image bytes bound by SHA-256, missing/unreadable/mutation pre-submit, controlled single-submit/ambiguous no retry.
- T14–T17: B04 current output availability vs historical DownloadRecord, export recheck, Qt handoff guard.
- T18–T21: B05 Windows atomic no-overwrite publication, unique .part, concurrent attempts, unsupported filesystem, publish-success/storage-failure manual recovery.
- T22–T25: B06 SQLite timezone-aware created/imported timestamps, isolated corruption, true offset order, source DB checksum unchanged.
- New R04 contract tests ensure all 25 case IDs remain tied to actual pytest functions. This is a *linkage guard*, **not a substitute for behavioral execution**. The official quality job executes all test suites and all prior integration/Qt tests.
- Existing non-numbered tests exercise keyring masking, bounded read-only Agent, SQLite legacy job migration, user-supplied package safety, UI heartbeat, safe download idempotency, Hasil manifest compatibility, etc.

## Fresh official main CI, source `baf3257b293f6b05b4cdbca7e9f3d4aa1272d218`
| Stage | Job ID | Status |
|---|---|---|
| quality — Python 3.14.7, uv 0.12.23, Ruff format/lint, mypy 81 source files, architecture | `113142594077` | **PASS** |
| pytest unit/contract/integration/smoke/UI | `113142594077` | **192 passed** |
| frozen UI capture/compare of 30 approved states | `113142876236` | **PASS 30/30** |
| staged Chromium, Chromium smoke, Windows portable onedir ZIP and executable smoke | `113143035521` | **PASS** |

Artifact verification (metadata verified from *fresh official main run*, expiring artifacts not guaranteed backups):
- Windows: ID `11527552603`, name `Flow-Otomatis-step12-i12-01-restart-proof-win-x64`, 435,725,819 bytes, SHA-256 `0ae8a7451acab9c7ed141df0248cb3090831c047ce37f3d14ea00a822942c1dd`, expires `2026-10-22T04:06:30Z`.
- Frozen UI: ID `11527787528`, 3,316,911 bytes, SHA-256 `9092dcc7acf074d496aeb57e6c11a1adb409ba25dc29443dcd585f5c526982dd`, expires `2026-10-22T04:03:15Z`.
- PR source run artifacts: Windows `11527174193` / `26a8288068527e0d73b40695ff0442bbad0423a43176c25c2e3493e73b0edc9c` and frozen UI `11527088939` / `22b25b3b14d4838d3e8f3ed1fceffc4a9c15a1103962fbdd4af6049d19a786d1`. These are **not** the final main artifacts.
- Verify source SHA against the run's `head_sha`, not against the later docs-only status update commit.

## Security and deployment boundaries
- R04 did not access real Gemini API keys, export browser cookies/tokens, automate user login, or invoke Google Flow live Generate/Download. Only synthetic/offline regression and official Windows packaging.
- PR file diff contains only new test matrix + audit documentation; neither contains a live credential. This is **not** a claim of independent forensic secret scanning of every historical repo file or artifact.
- GUI must still be validated by the owner on Windows 11 normal Chrome: manual sign-in → READY → app close/reopen → same profile READY + `Validasi restart: Lulus`.
- Only *after* this proof plus authorization may a separate live one-Scene Generate and later live Download be developed/tested. Never guess selectors; never silently retry ambiguity.
- `UNAVAILABLE` is a conservative v1.0 manifest status extension; strict-enum third-party consumers are **not independently certified**.
- Atomic no-clobber hardlinks require filesystem support (same-volume NTFS/POSIX); unsupported drives/shares fail closed with manual reconciliation.
- Original standalone ASTRA repro harness was not available; repository regression matrix plus combined CI is the actual proof.

## Audit disposition
**B01–B06: CLOSED locally, R00–R04 COMPLETE/PASS.**
The app's **STEP 12 overall live product gate remains BLOCKED** by real-account restart validation and separate authorization. Offline completion does not imply that the app can already operate Google Flow live.
