# SOL C00–C01 — Google Session Runtime Freshness (9 Oct 2026)

## Baseline and sources
- Repo: `inoriko920-dev/Flow-Otomatis`; source `main` `5b74d686d44ff67f7473fe46d8fcb7a9904618bf`.
- PR #31 UI/local Workspace is Draft at `c4552afa867be1c51f9a376215f6eb803ad15d9e`. None of the C01 canonical Google Session files were changed in that PR; this branch starts from `main` instead of copying unfinished PR #31.
- PR #25 approved UI binary archive; #27 six original planning DOCX + G0 source selection; #26 D01–D06 architecture owner-approved **design**, all still Draft and not merged.
- Referenced `AGENTS.md`, `PROJECT_STATE.md`, `TASKS.md`, ADR-017, ADR-021, ADR-023, and ASTRA C00–C04 handoff dated 2026-10-09.
- **No merge** and no claim of strict G0 completion; outstanding draft documents/UI remain integration prerequisites.

## Capability matrix (only evidence-based)
| Function | Current state |
|---|---|
| Manual Google login | Production installed-Chrome code exists; owner historically reported manual login success |
| Fresh session on every launch | C01 code change in this branch; awaiting official Windows CI/owner validation |
| Google Flow access | Reachability-only preflight exists; no production UI wiring |
| Flow workspace and account identity | Not positively verified |
| Flow Generate/Download | Live selector/wiring incomplete, BLOCKED |
| Multiaccount | Offline simulation only; no live automation authority |

## C01 changes (isolated safety fix)
- `profile.json` READY from an older application process is represented as effective UNKNOWN until the current worker successfully probes. History stays on disk unchanged.
- Current-instance READY rights are revoked **before** starting a new check and on manual-login, cancel, profile-delete, and shutdown; unsuccessful/error probes never restore rights.
- `get_restart_gate` consumes effective runtime state, not persisted history alone. Historical `restart-proof.json` remains readable.
- Provider-side `RestartGatedGenerationProvider` continues to fail closed with zero downstream calls when the effective gate is false.
- No cookies/passwords/tokens in metadata, diagnostic artifacts, or source. No live requests or credits used by this change.

## Tests changed and required gates
- `tests/integration/test_google_session_worker.py`: historical READY is UNKNOWN upon reload; A/B/C third startup without probe is blocked; failed recheck, login, cancel, shutdown revoke readiness; and downstream remains zero before C's own probe.
- Existing `tests/unit/test_google_session_restart_gate.py` and `tests/unit/test_restart_gated_generation_provider.py` remain compatible; runtime enforcement is in the canonical worker.
- Official remaining: `uv sync --frozen`, Ruff, mypy, architecture guard, unit/integration/Qt, 30 frozen UI regression, portable Windows build/smoke and exact-SHA evidence.
- Gate C01 must not be marked PASS until tests and Windows CI succeed.
- G0 integration, C02 Flow identity preflight, C03 UI, C04 real Windows/owner account still outstanding.
- No Google Flow mutation, release or merge authorized.
