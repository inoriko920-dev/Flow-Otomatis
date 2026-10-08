# SOL R00 — New ASTRA Audit Baseline and Code Evidence
Date: 8 October 2026 WIB
Scope: Flow-Otomatis, STEP 12, documentation-only package R00.
Main SHA inspected: `0b9e2c4f63a9c0fdab0fe255830964a0e2fb6b39`.
ASTRA audit SHA for the uploaded original DOCX: SHA-256 `5481a09b85219615169c285d6bfd42bcc7398bcf881a73a604f2e7a351444fda`, 48,799 bytes.
Original document: `ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-08.docx`.
Git blob SHA: `0a7bd29f26e2f8b3bd489ba4e5b82cff47362fb4`.
The original DOCX is committed byte-identically; it is NOT a simplified or regenerated copy.

## Scope and source of evidence
- Head comparison: `main` is still the exact ASTRA audit commit, so all six code paths are unmodified after audit.
- SOL inspected the actual main-branch source and existing repository contract/architecture files.
- ASTRA's DOCX documents five synthetic service/adapter reproductions and one isolated Qt callback-body reproduction.
- The separate `reproduction_results.json` and `reproduce_findings.py` mentioned by ASTRA were **not included** with the user upload and have **not** been committed. These must not be represented as available executable evidence.
- No SOL live test, Windows regression, full pytest, key health call, Flow submission, or original ASTRA harness rerun was performed in R00.

## Traceability by finding
| ID | Code confirmed on main | Why it remains relevant | Status |
|---|---|---|---|
| B01 | `application/services/gemini_keys.py:check_health` calls `repository.save(updated)`; `sqlite_gemini_key_repository.py:save` upserts `is_active` and deactivates other rows when true | An old health completion may override newer manual selection and re-create deleted metadata | OPEN → R01 |
| B02 | `presentation/main_window.py:_GeminiAgentSignals`, `select_workspace_scene`, `_on_gemini_agent_answered`, `_on_gemini_agent_failed` | Reply/error has no immutable request/context ID; old completion unconditionally resets busy and writes currently displayed answer | OPEN → R01 |
| B03 | `application/services/local_generation_queue.py:_stale_reason` checks stored `scene.image_exists` / request fingerprint; it does not freshly verify physical folder/ZIP bytes before `mark_submit_started` | Deleted or modified image can escape queue validation | OPEN → R02 |
| B04 | `application/services/local_results.py:snapshot` passes historic download state to `domain/result/model.py:handoff_ready`; `result_manifest_writer.py` exports that state | Deleted, unreadable or empty output can still be marked downloaded and handoff-ready | OPEN → R03 |
| B05 | `workers/browser/google_flow_download.py:download` prechecks `.exists()`, then `os.replace(partial_path, final_path)` | An existing final created during a download can be overwritten | OPEN → R03 |
| B06 | `sqlite_workspace_repository.py:_decode_workspace` parses ISO without aware-only invariant; `scan_recent` sorts imported_at outside per-project error handling | Mixed naive and aware timestamps can raise TypeError for the entire list | OPEN → R02 |

## Approved implementation order and tests
- R01 B01+B02: T01–T08, SQLite real DB + deterministic Events + Qt signal/lifecycle tests.
- R02 B03+B06: T09–T13 + T22–T25, real temporary folder/ZIP and SQLite isolation.
- R03 B04+B05: T14–T21, output effective-status + actual Windows filesystem collision tests.
- R04: full frozen-environment CI, UI 30/30, Windows portable, source-SHA and artifact hashes.

## Gate
R00 checks: HEAD verified; source owners mapped; original audit DOCX committed; decisions recorded; tasks/state/handoff updated.
All B01–B06 remain **OPEN** until positive regression tests pass. Live Flow remains **BLOCKED**.
