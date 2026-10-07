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
- Automated CI baseline remains PASS.
- Real user-owned Google login/restart persistence must still be tested on the packaged Windows app.

### I12-02A — Deterministic Submit Contract & Ambiguous-Submit Guard
- Status: PASS.
- Tested implementation SHA: `90fafb83821ff7ec82c3253d046293b780220edb`.
- CI run: `37603714336` — SUCCESS.
- Quality job: `112734004875` — SUCCESS.
- UI visual job: `112734322641` — SUCCESS.
- Windows package job: `112734665287` — SUCCESS.

Delivered:
- one-submit Google Flow driver contract;
- explicit ACCEPTED / SAFE_FAILURE / AUTH_REQUIRED / CANCELLED / AMBIGUOUS evidence;
- no automatic provider retry;
- stable remote id required before GENERATED;
- ATTENTION_REQUIRED durable job state;
- ambiguous/auth outcomes block the queue;
- second queued Scene is not submitted while attention is unresolved;
- Hasil UI/metrics understand ATTENTION_REQUIRED;
- no live selectors or Google Flow mutation implemented.

Automated evidence:
- Ruff format/lint: PASS.
- mypy strict: PASS — 56 source files.
- architecture guard: PASS.
- pytest: 53 passed.
- UI regression: 30/30 PASS.
- similarity: 0.6344–0.9643 at threshold 0.55.
- Chromium stage/smoke: PASS.
- PyInstaller onedir: PASS.
- portable application smoke: PASS.
- UI evidence artifact:
  - ID: `11473099652`
  - digest: `34de8d0b0ddd910c40017b46c7e66a4fd37a3ac9e6107d720891296eb5253726`
- Windows artifact:
  - ID: `11473888042`
  - size: `435454484` bytes
  - digest: `0d5eabc603acba99c0e7d5c09e3adcec51135e7a0bf8c37bdde97ad4ac332c99`

### I12-02B — Live Google Flow Playwright Driver
- Status: BLOCKED pending successful I12-01 real-account validation + next explicit `lanjutkan`.
- First live slice:
  - one Scene only;
  - use existing GenerationRequest;
  - reuse one authorized user-owned profile;
  - current verified Flow UI selectors only;
  - exactly one mutating submit attempt;
  - timeout/cancel classification;
  - ambiguous outcome → ATTENTION_REQUIRED;
  - never silently resubmit.

### I12-03 — Live Result Detection & Download Adapter
- Status: PLANNED after I12-02B.
- Keep Generate and Download separate.

### I12-04 — Gemini AI Agent / Key Integration
- Status: PLANNED after I12-03.
- Keyring-backed secrets, masked UI, bounded permissions.

## STEP 12 safety boundary
- No CAPTCHA/MFA bypass.
- No credential/session export.
- No automatic account/key rotation designed to evade quotas/rate limits/free-credit limits.
- No silent retry of potentially mutating generation submissions.
- Do not guess live Flow selectors.
