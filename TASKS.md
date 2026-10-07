# TASKS — Flow-Otomatis

## STEP 08 — Repository Foundation
Status: PASS.

## STEP 09 — App Shell/UI Implementation
Status: PASS.

## STEP 10 — Minimum End-to-End Vertical Slice
Status: PASS.

## STEP 11 — Feature Implementation Waves
Status: PASS.
- Scene planning/readiness: PASS.
- Local Project Hub/recovery: PASS.
- Durable serial local queue/fake provider: PASS.
- Local results/handoff manifest: PASS.

## STEP 12 — Integrations & External Services
Status: IN PROGRESS.

### I12-01 — Authorized Google Session / Manual Login Lifecycle
- Status: AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING.
- Priority/Risk: P0 / HIGH.
- Tested implementation SHA: `70dd90b7e08c0f0b9261021a4f02966daf046c60`.
- CI run: `37602579445` — SUCCESS.
- Quality job: `112730274502` — SUCCESS.
- UI visual job: `112730670338` — SUCCESS.
- Windows package job: `112730961256` — SUCCESS.

Delivered:
- persistent user-owned local Google profile/session directories;
- official manual Google login surface;
- explicit Ready / Needs Login / Unknown / Error state;
- credential-free application port/service contract;
- Browser Worker-only Playwright ownership;
- real Profil Google and Bantuan Login runtime binding;
- profile-scoped cancel/delete and app shutdown cleanup;
- no password/token/cookie/session export;
- manual MFA/CAPTCHA only.

Automated evidence:
- Ruff format/lint: PASS.
- mypy strict: PASS — 55 source files.
- architecture guard: PASS.
- pytest: 46 passed.
- UI regression: 30/30 PASS.
- similarity: 0.6344–0.9643 at threshold 0.55.
- Chromium stage/smoke: PASS.
- PyInstaller onedir: PASS.
- portable application smoke: PASS.
- UI evidence artifact:
  - ID: `11473523196`
  - digest: `fa5ab49c244259108cd6ae06dcc69ad076bd9cce748a36662e6c3172e9d9f3ff`
- Windows artifact:
  - ID: `11473218426`
  - size: `435450690` bytes
  - digest: `21cf2df1f869e31b5632e3cf8320cd08f3fcc50c5ca5088f226f220cdb4c6338`

Manual acceptance still required:
- real user-owned Google login succeeds in packaged app;
- Cek Ulang Sesi reaches Siap after login;
- closing/reopening app reuses the same local browser profile when Google's session remains valid;
- logout/expired session returns to Needs Login/attention without bypass;
- no credentials/session secrets appear in diagnostics or project/export artifacts.

### I12-02 — Deterministic Google Flow Generation Adapter
- Status: BLOCKED pending I12-01 live manual acceptance + next explicit `lanjutkan`.
- Goal: execute exactly one existing GenerationRequest through the Browser Worker.
- Required before any broader queue execution:
  - one Scene only;
  - explicit timeout/cancel;
  - safe idempotency;
  - ambiguous-submit protection;
  - no silent retry of a potentially mutating submit.

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
- Keep Generate and Download separate.
- Do not start I12-02 until I12-01 live manual validation is accepted and the product owner says `lanjutkan`.
