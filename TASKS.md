# TASKS — Flow-Otomatis

## STEP 08 — Repository Foundation
Status: PASS.

## STEP 09 — App Shell/UI Implementation
Status: PASS.
- Last tested STEP 09 SHA: ee90740ba6e620af1107d73b19b6753395aa26bd.
- Final STEP 09 CI: 37587748975 — SUCCESS.
- 30/30 frozen UI visual gate: PASS.

## STEP 10 — Minimum End-to-End Vertical Slice
Status: PASS.
- Import/validate episode package → persisted real workspace proven.
- Safe package validation and SQLite persistence proven.
- Frozen Validation/Workspace UI bound to real state.
- Final STEP 10 CI: 37590300417 — SUCCESS.

## STEP 11 — Feature Implementation Waves
Status: PASS.
Last tested implementation SHA: 75a896ccf3754a225414c34de9f88d5d9a8b5581.
Final CI run: 37597279499 — SUCCESS.

### W11-01 — Scene Planning & Readiness
- Status: PASS.
- Persist Flow duration selection 4/6/8/10.
- Reject selection shorter than Target.
- Keep Target immutable.
- Real approved-image rescan/remap evidence.
- Recompute readiness deterministically.
- Frozen Workspace/Scene Inspector controls wired to application commands.
- Save/reload persistence verified.

### W11-02 — Local Project Hub / Recent Project / Recovery
- Status: PASS.
- Persisted local projects listed newest first.
- Existing project can be reopened from real Project Hub.
- Local persisted-state recovery verified.
- No external-provider recovery claim.

### W11-03 — Durable Serial Queue / Fake Provider
- Status: PASS.
- Durable local generation jobs in project SQLite.
- R1 serial claim enforced.
- Queue preparation idempotent.
- Provider-neutral request/result contract exists.
- Fake-provider queue execution verified.
- Live Google Flow provider remains out of scope.

### W11-04 — Local Results / Handoff Manifest
- Status: PASS.
- Generate and Download tracked separately.
- Download outcomes persist in project SQLite.
- Download success requires GENERATED state and an existing local file.
- Real Hasil UI renders persisted facts.
- FLOW_OTOMATIS_RESULT.json atomic export verified.
- Handoff manifest excludes credential/cookie/token data.

### STEP 11 regression / Windows evidence
- Ruff format/lint: PASS.
- mypy strict: PASS — 51 source files.
- architecture guard: PASS.
- pytest: 43 passed.
- UI regression: 30/30 PASS.
- Similarity: 0.6344–0.9643 at threshold 0.55.
- Chromium stage/smoke: PASS.
- PyInstaller onedir: PASS.
- Portable application smoke: PASS.
- UI evidence artifact ID: 11471336385.
- UI artifact digest: 738549ef6b86e9c51530e604ac9758914eea823b2fdd2181df8cc831f3d35d02.
- Windows artifact ID: 11471780918.
- Windows artifact digest: b85a3541f03524d65c439912dd4c7afd98ab1727c7661b5cf5487e73895b481d.

## NEXT — STEP 12: Integrations & External Services
Status: READY, NOT STARTED.

### I12-01 — Authorized Google Session / Manual Login Lifecycle
- Status: READY.
- Priority/Risk: P0 / HIGH.
- Scope:
  - persistent user-owned Google profile/session contexts;
  - manual official Google login;
  - explicit session status/check/recovery;
  - MFA/CAPTCHA remains manual;
  - no password/token/cookie extraction into project/log/export;
  - timeout/cancel/diagnostic/redaction contract.
- Acceptance:
  - create/open an authorized profile context;
  - detect ready vs needs-login deterministically;
  - restart preserves authorized browser context where provider/session allows it;
  - logout/expired state becomes Needs Attention without bypass;
  - diagnostics contain no credentials.

### I12-02 — Deterministic Google Flow Generation Adapter
- Status: PLANNED after I12-01.
- Goal: execute exactly one existing GenerationRequest through the Browser Worker with timeout, cancel, idempotency, and ambiguous-submit protection.

### I12-03 — Live Result Detection & Download Adapter
- Status: PLANNED after I12-02.
- Goal: detect real Flow completion and download/verify local video before marking Download success.

### I12-04 — Gemini AI Agent / Key Integration
- Status: PLANNED after I12-03.
- Goal: keyring-backed Gemini integration with masked key UI, bounded tools/context, and explicit permissions.

## STEP 12 safety boundary
- No CAPTCHA/MFA bypass.
- No credential/session export.
- No automatic account/key rotation designed to evade quotas/rate limits/free-credit limits.
- Do not silently retry potentially mutating generation submissions when outcome is ambiguous.
- Do not start STEP 12 until the product owner says "lanjutkan".
