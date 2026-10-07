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
- Official Flow reachability/auth preflight and shared persistent context pool proven.

### I12-02B2-PRECHECK — Pre-Submit Request Guard
- Status: PASS.
- Tested implementation SHA: `827c8f756b44cef94d5edeb5588fc1979cad8b07`.
- CI run: `37605969763` — SUCCESS.
- Quality: `112741397608` — SUCCESS.
- UI visual: `112741803066` — SUCCESS.
- Windows package: `112742072939` — SUCCESS.

Delivered:
- GenerationRequestValidationError;
- PreparedGoogleFlowRequest;
- pure pre-submit request normalization/validation;
- image/prompt/episode/scene required;
- target duration >0;
- Flow duration restricted to 4/6/8/10;
- target duration cannot exceed Flow duration;
- exact frozen model/resolution/aspect-ratio validation;
- invalid request stops before driver invocation;
- no live Flow mutation.

Evidence:
- Ruff format/lint: PASS.
- mypy strict: PASS — 61 source files.
- architecture guard: PASS.
- pytest: 75 passed.
- UI regression: 30/30 PASS.
- similarity: 0.6344–0.9643.
- Chromium stage/smoke: PASS.
- PyInstaller onedir: PASS.
- portable smoke: PASS.
- UI artifact:
  - ID: `11474916989`
  - digest: `4b53a1d7f922664dab277ecfa005ebbc9bddf72373772cd59cec6d2641498e5f`
- Windows artifact:
  - ID: `11474334971`
  - size: `435465430` bytes
  - digest: `f719cbd338b95febec821788dbdef8f1693947a319d2ad8714c4fd81aa7d2d8a`

### I12-02B2-LIVE — Live One-Scene Google Flow Submit Driver
- Status: BLOCKED pending successful I12-01 real-account validation.
- Start only after successful manual validation + next explicit `lanjutkan`.
- Use current verified authorized Flow UI only.
- Exactly one mutating attempt.
- No silent retry.
- Ambiguous outcome → ATTENTION_REQUIRED.
- No result download in this slice.

### I12-03 — Live Result Detection & Download Adapter
- Status: PLANNED after I12-02B2-LIVE.

### I12-04 — Gemini AI Agent / Key Integration
- Status: PLANNED after I12-03.

## STEP 12 safety boundary
- No CAPTCHA/MFA bypass.
- No credential/session export.
- No automatic account/key rotation to evade limits.
- No guessed live generation selectors.
- No silent retry after ambiguous mutation.
