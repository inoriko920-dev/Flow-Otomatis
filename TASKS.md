# TASKS — Flow-Otomatis

## STEP 08 — Repository Foundation
Status: PASS.

## STEP 09 — App Shell/UI Implementation
Status: PASS.

## STEP 10 — Minimum End-to-End Vertical Slice
Status: PASS.

## STEP 11 — Feature Implementation Waves
Status: PASS.

## STEP 12 — Integrations & External Services
Status: IN PROGRESS.

### I12-01 — Authorized Google Session / Manual Login Lifecycle
- Status: AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING.
- Real Google account login/restart persistence still requires product-owner validation.

### I12-02A — Deterministic Submit Contract & Ambiguous-Submit Guard
- Status: PASS.
- One-submit contract and ATTENTION_REQUIRED anti-duplicate behavior proven.

### I12-02B1 — Read-Only Google Flow Preflight
- Status: PASS.
- Tested implementation SHA: `8ebd5a5e048c1a3c606c2ace4ddf17c8ef510780`.
- CI run: `37604743253` — SUCCESS.
- Quality: `112737380299` — SUCCESS.
- UI visual: `112737696541` — SUCCESS.
- Windows package: `112737987743` — SUCCESS.

Delivered:
- official Flow read-only navigation target;
- REACHABLE / AUTH_REQUIRED / UNAVAILABLE / UNKNOWN / ERROR;
- existing local profile validation;
- no upload, prompt typing, selector locking, or generation click;
- shared persistent Playwright context pool for session + Flow preflight;
- no UI redesign.

Evidence:
- Ruff format/lint: PASS.
- mypy strict: PASS — 60 source files.
- architecture guard: PASS.
- pytest: 59 passed.
- UI regression: 30/30 PASS.
- similarity: 0.6344–0.9643.
- Chromium stage/smoke: PASS.
- PyInstaller onedir: PASS.
- portable smoke: PASS.
- UI artifact:
  - ID: `11473953895`
  - digest: `37de328dbe47abd5ba8a9114c9a0999d3e1be8c46d46534cd9a729499f69465b`
- Windows artifact:
  - ID: `11474421936`
  - size: `435464521` bytes
  - digest: `0cf17a7590251cfa775b502401eddaaf5b3a1bfef1f445229844387b13bced16`

### I12-02B2 — Live One-Scene Google Flow Submit Driver
- Status: BLOCKED pending successful I12-01 real-account validation.
- Start only after next explicit `lanjutkan` following successful manual validation.
- Exactly one mutating attempt.
- No silent retry.
- Ambiguous outcome → ATTENTION_REQUIRED.
- No download/result detection in this slice.

### I12-03 — Live Result Detection & Download Adapter
- Status: PLANNED after I12-02B2.

### I12-04 — Gemini AI Agent / Key Integration
- Status: PLANNED after I12-03.

## STEP 12 safety boundary
- No CAPTCHA/MFA bypass.
- No credential/session export.
- No automatic account/key rotation to evade limits.
- No guessed live generation selectors.
- No silent retry after ambiguous mutation.
