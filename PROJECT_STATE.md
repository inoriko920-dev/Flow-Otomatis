# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Factory STEP active: STEP 12 — Integrations & External Services
- STEP 12 status: IN PROGRESS
- I12-01 — Authorized Google Session / Manual Login Lifecycle: AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING
- I12-02A — Deterministic Submit Contract & Ambiguous-Submit Guard: PASS
- I12-02B1 — Read-Only Google Flow Preflight: PASS
- I12-02B2 — Live One-Scene Google Flow Submit Driver: BLOCKED pending real-account session validation
- Last tested implementation SHA: 8ebd5a5e048c1a3c606c2ace4ddf17c8ef510780
- I12-02B1 CI run: 37604743253 — SUCCESS
- Quality job: 112737380299 — SUCCESS
- UI regression job: 112737696541 — SUCCESS
- Windows package job: 112737987743 — SUCCESS
- UI evidence artifact ID: 11473953895
- UI evidence digest: sha256:37de328dbe47abd5ba8a9114c9a0999d3e1be8c46d46534cd9a729499f69465b
- Windows artifact ID: 11474421936
- Windows artifact size: 435464521 bytes
- Windows artifact digest: sha256:0cf17a7590251cfa775b502401eddaaf5b3a1bfef1f445229844387b13bced16
- Live Google account login/session persistence: NOT YET VALIDATED
- Live Flow upload/prompt/generate/result/download: NOT TESTED

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
  - I12-02B2: BLOCKED pending I12-01 live validation
  - I12-03: PLANNED after live generation submit
  - I12-04: PLANNED after I12-03

## I12-02B1 delivered
This slice remains deliberately read-only.

Delivered:
- verified official Google Flow desktop surface: https://labs.google/fx/tools/flow
- new application contract:
  - GoogleFlowAccessState
  - GoogleFlowAccessProbe
  - GoogleFlowPreflightPort
  - GoogleFlowPreflightService
- read-only states:
  - REACHABLE
  - AUTH_REQUIRED
  - UNAVAILABLE
  - UNKNOWN
  - ERROR
- GoogleFlowPreflightWorker validates only an existing local Google profile.
- Playwright preflight performs navigation only.
- It does not:
  - upload an image;
  - type a prompt;
  - choose model/duration/resolution;
  - inspect or lock generation-control selectors;
  - click Create/Generate;
  - consume Flow credits intentionally.
- HTTP 4xx/5xx is surfaced as UNAVAILABLE.
- redirect to accounts.google.com is surfaced as AUTH_REQUIRED.
- labs.google host is surfaced only as REACHABLE, not as proof generation works.
- timeout becomes UNKNOWN.
- browser failure becomes ERROR.
- all diagnostics remain sanitized.
- a shared PlaywrightPersistentContextPool now owns one persistent Chromium context per profile id.
- Google login/session driver can use the same context pool as Flow preflight, preventing competing contexts against the same browser-data directory.
- existing UI remains unchanged; frozen UI source-of-truth was preserved.

## I12-02B1 automated evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 60 source files.
- architecture guard: PASS.
- pytest: 59 passed.
- Frozen UI regression: 30/30 PASS.
- Visual similarity range: 0.6344–0.9643 at threshold 0.55.
- Chromium staging/smoke: PASS.
- PyInstaller onedir: PASS.
- Portable application smoke: PASS.
- UI evidence: Flow-Otomatis-step12-i12-02b1-readonly-preflight-ui-evidence.
- Windows artifact: Flow-Otomatis-step12-i12-02b1-readonly-preflight-win-x64.

## Critical boundary
I12-02B1 proves architecture and read-only browser behavior only.
It does NOT prove:
- the product owner's Google account is authenticated;
- the Flow app surface behind that account is usable;
- a project can be created/opened;
- generation controls are stable;
- live upload/prompt/model/duration selection works;
- a real Generate action is safe;
- remote result detection/download works.

Do not infer generation readiness from REACHABLE.

## Architecture/product rules still frozen
- Browser automation belongs under Browser Worker.
- One user-owned profile maps to one persistent Chromium context.
- No CAPTCHA/MFA bypass.
- No password/cookie/token/session export.
- No hidden account/key rotation or quota/rate-limit evasion.
- Never auto-retry a mutating submit with ambiguous outcome.
- ATTENTION_REQUIRED blocks subsequent queue claims.
- Generate and Download remain separate.
- STEP 09 UI cannot be silently redesigned.

## Required manual validation before I12-02B2
Using the Windows artifact:
1. open Profil Google;
2. create/open a user-owned profile;
3. manually complete Google login;
4. Cek Ulang Sesi must report Siap;
5. close and reopen the app;
6. same profile must remain available and report Siap where Google retains the session.

Do not share passwords, MFA codes, cookies, browser-data, or tokens.

## Next exact action
Do not implement the mutating Flow submit driver until the real-account session gate above passes.
After successful validation and an explicit “lanjutkan”, start I12-02B2 for one Scene only:
- current verified Flow UI only;
- exactly one mutating submit attempt;
- no silent retry;
- ambiguous outcome → ATTENTION_REQUIRED;
- no result download and no Gemini in the same slice.
