# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Factory STEP active: STEP 12 — Integrations & External Services
- STEP 12 status: IN PROGRESS
- I12-01 — Authorized Google Session / Manual Login Lifecycle: AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING
- I12-02A — Deterministic Submit Contract & Ambiguous-Submit Guard: PASS
- I12-02B1 — Read-Only Google Flow Preflight: PASS
- I12-02B2-PRECHECK — Pre-Submit Request Guard: PASS
- I12-02B2-LIVE — Live One-Scene Google Flow Submit Driver: BLOCKED pending real-account session validation
- Last tested implementation SHA: 827c8f756b44cef94d5edeb5588fc1979cad8b07
- I12-02B2-PRECHECK CI run: 37605969763 — SUCCESS
- Quality job: 112741397608 — SUCCESS
- UI regression job: 112741803066 — SUCCESS
- Windows package job: 112742072939 — SUCCESS
- UI evidence artifact ID: 11474916989
- UI evidence digest: sha256:4b53a1d7f922664dab277ecfa005ebbc9bddf72373772cd59cec6d2641498e5f
- Windows artifact ID: 11474334971
- Windows artifact size: 435465430 bytes
- Windows artifact digest: sha256:f719cbd338b95febec821788dbdef8f1693947a319d2ad8714c4fd81aa7d2d8a
- Live Google account login/session persistence: NOT YET VALIDATED
- Live Flow upload/prompt/settings/generate/result/download: NOT TESTED

## STEP status
- STEP 00: PASS
- STEP 01: PASS
- STEP 02: PASS
- STEP 03: PASS
- STEP 04: PASS
- STEP 05: PASS_WITH_PROVISIONAL
- STEP 06: PASS_WITH_PROVISIONAL
- STEP 07: PASS_WITH_PROVISIONAL
- STEP 08: PASS
- STEP 09: PASS
- STEP 10: PASS
- STEP 11: PASS
- STEP 12: IN PROGRESS
  - I12-01: AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING
  - I12-02A: PASS
  - I12-02B1: PASS
  - I12-02B2-PRECHECK: PASS
  - I12-02B2-LIVE: BLOCKED pending I12-01 live validation
  - I12-03: PLANNED after live generation submit
  - I12-04: PLANNED after I12-03

## I12-02B2-PRECHECK delivered
This slice validates the frozen generation contract before any live Browser Worker mutation.

Delivered:
- new GenerationRequestValidationError.
- new pure request preparation module: `workers/browser/google_flow_request_plan.py`.
- new immutable `PreparedGoogleFlowRequest`.
- `prepare_google_flow_request(...)` trims and validates provider-neutral request values.
- required non-empty values:
  - episode_id;
  - scene_id;
  - image_file;
  - motion_prompt.
- target duration must be >0 seconds.
- Flow duration is limited to exactly:
  - 4;
  - 6;
  - 8;
  - 10 seconds.
- target duration must not exceed Flow duration.
- frozen generation settings must match:
  - model: Omni Flash 1.1;
  - resolution: 720p;
  - aspect ratio: 16:9.
- invalid requests fail before `GoogleFlowGenerationDriver.submit_one(...)` is invoked.
- fixture evidence explicitly proves driver call count stays zero for invalid requests.
- no live selector, upload, prompt input, settings click, project mutation, or Generate click was added.

## Why this guard exists
A malformed request must not reach a mutating browser action because it could:
- consume a generation credit with the wrong settings;
- produce an unusable Scene;
- create an ambiguous submit that cannot be safely retried.

The provider therefore validates the frozen contract before any future live driver is allowed to submit.

## I12-02B2-PRECHECK automated evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 61 source files.
- architecture guard: PASS.
- pytest: 75 passed.
- Frozen UI regression: 30/30 PASS.
- Visual similarity range: 0.6344–0.9643 at threshold 0.55.
- Chromium staging/smoke: PASS.
- PyInstaller onedir build: PASS.
- Portable application smoke: PASS.
- UI evidence: `Flow-Otomatis-step12-i12-02b2-precheck-ui-evidence`.
- Windows artifact: `Flow-Otomatis-step12-i12-02b2-precheck-win-x64`.

## Critical boundary
I12-02B2-PRECHECK does NOT prove:
- the product owner's Google account is authenticated;
- the Google session survives application restart;
- Flow project creation/opening works;
- current live generation selectors are known;
- live image upload works;
- live prompt entry works;
- live model/duration/resolution selection works;
- Generate can be safely clicked;
- a stable remote result id can be discovered;
- result detection/download works.

Do not label Google Flow generation as operational until live validation succeeds.

## Architecture/product rules still frozen
- Browser automation belongs under Browser Worker.
- One user-owned profile maps to one persistent Chromium context.
- No CAPTCHA/MFA bypass.
- No password/cookie/token/session export.
- No hidden account/key rotation or quota/rate-limit evasion.
- Never auto-retry a mutating submit with ambiguous outcome.
- ATTENTION_REQUIRED blocks subsequent queue claims.
- Generate and Download remain separate.
- Omni Flash 1.1 • 720p • 16:9.
- Flow durations are 4/6/8/10.
- Audio/SRT Target is authoritative.
- STEP 09 UI cannot be silently redesigned.

## Required manual validation before I12-02B2-LIVE
Using the Windows artifact:
1. open Profil Google;
2. create/open a user-owned profile;
3. manually complete Google login;
4. Cek Ulang Sesi must report Siap;
5. fully close the app;
6. reopen the app;
7. same profile must remain available and Cek Ulang Sesi must report Siap where Google retained the session.

Do not share passwords, MFA codes, cookies, browser-data, or tokens.

## Next exact action
Do not implement the mutating live Flow driver until the real-account session gate above passes.

After successful validation and an explicit “lanjutkan”, start I12-02B2-LIVE for one Scene only:
- inspect the current authorized Flow UI;
- lock only verified current selectors;
- exactly one mutating submit attempt;
- no silent retry;
- ambiguous outcome → ATTENTION_REQUIRED;
- no result download in this slice;
- no Gemini integration in this slice.
