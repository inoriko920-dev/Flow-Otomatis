# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Factory STEP active: STEP 12 — Integrations & External Services
- STEP 12 status: IN PROGRESS
- I12-01 — Authorized Google Session / Manual Login Lifecycle: AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING
- I12-02A — Deterministic Submit Contract & Ambiguous-Submit Guard: PASS
- I12-02B — Live Google Flow Playwright Driver: BLOCKED pending I12-01 live manual validation
- Last tested implementation SHA: 90fafb83821ff7ec82c3253d046293b780220edb
- I12-02A CI run: 37603714336 — SUCCESS
- Quality job: 112734004875 — SUCCESS
- UI regression job: 112734322641 — SUCCESS
- Windows package job: 112734665287 — SUCCESS
- UI regression artifact ID: 11473099652
- UI regression artifact digest: sha256:34de8d0b0ddd910c40017b46c7e66a4fd37a3ac9e6107d720891296eb5253726
- Windows portable artifact ID: 11473888042
- Windows portable artifact uploaded size: 435454484 bytes
- Windows portable artifact digest: sha256:0d5eabc603acba99c0e7d5c09e3adcec51135e7a0bf8c37bdde97ad4ac332c99
- Live Google login/session persistence against a real account: NOT YET VALIDATED
- Live Google Flow submit/generation/download and Gemini provider: NOT TESTED

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
  - I12-02B: BLOCKED pending I12-01 live manual validation
  - I12-03: PLANNED after live I12-02
  - I12-04: PLANNED after I12-03

## I12-02A delivered contract/preflight
I12-02A deliberately adds **no live Google Flow selectors or mutation**. It prepares deterministic semantics so a future live Browser Worker cannot silently duplicate a generation request.

Delivered:
- provider exception taxonomy:
  - GenerationProviderError
  - GenerationSubmissionAmbiguousError
  - GenerationAuthenticationRequiredError
  - GenerationCancelledError
- new durable generation state:
  - ATTENTION_REQUIRED
- SQLite queue behavior now refuses to claim another Scene while a RUNNING or ATTENTION_REQUIRED job exists.
- LocalGenerationQueueService maps:
  - ambiguous outcome → ATTENTION_REQUIRED;
  - auth required → ATTENTION_REQUIRED;
  - safe cancellation → FAILED with explicit cancelled diagnostic;
  - confirmed accepted submit with stable remote id → GENERATED;
  - ordinary safe provider failure → FAILED.
- Hasil view displays ATTENTION_REQUIRED as “Perlu Perhatian”.
- results attention metric counts ATTENTION_REQUIRED.
- `GoogleFlowGenerationProvider` introduced under Browser Worker boundary.
- `GoogleFlowGenerationDriver` protocol introduced for one-submit browser execution.
- sanitized driver evidence states:
  - ACCEPTED
  - SAFE_FAILURE
  - AUTH_REQUIRED
  - CANCELLED
  - AMBIGUOUS
- provider performs exactly one driver call; it contains no automatic retry loop.
- ACCEPTED without a stable remote_result_id is treated as AMBIGUOUS.
- fixture tests prove ambiguous first submit blocks the second queued Scene and prevents automatic resubmission.

## I12-02A automated evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 56 source files.
- architecture guard: PASS.
- pytest: 53 passed.
- Frozen UI regression: 30/30 PASS.
- Visual similarity range: 0.6344–0.9643 at threshold 0.55.
- Playwright Chromium staging/smoke: PASS.
- PyInstaller onedir build: PASS.
- Portable application smoke: PASS.
- UI evidence artifact: `Flow-Otomatis-step12-i12-02a-contract-ui-regression-evidence`.
- Windows artifact: `Flow-Otomatis-step12-i12-02a-contract-win-x64`.

## Live boundary remains blocked
I12-02A does **not** implement or claim:
- Google Flow selectors;
- clicking a real Generate/Create button;
- uploading to live Google Flow;
- real remote_result_id discovery;
- live timeout classification;
- live cancellation;
- result detection/download;
- real account/provider recovery.

No selector should be guessed from stale/public screenshots. The live driver must be built against the product owner's successfully authorized session and verified current Flow UI.

## Architecture/product rules still frozen
- CPython 3.14.x x64 + PySide6 Qt Widgets.
- Playwright Chromium belongs to dedicated Browser Worker/provider boundary.
- Presentation must not import Playwright/workers/infrastructure directly.
- Modular monolith + ports/adapters.
- SQLite per-project persistence.
- Browser session data belongs only to user-scoped Session root.
- PyInstaller onedir portable ZIP.
- Serial R1 generation queue.
- Omni Flash 1.1 • 720p • 16:9.
- Audio/SRT Target is authoritative.
- Flow duration values are 4/6/8/10.
- Generate and Download remain separate states.
- No CAPTCHA/MFA bypass.
- No credential/session export.
- No hidden account/key rotation or quota/rate-limit evasion.
- Never silently retry a mutating generation submit when provider outcome is ambiguous.
- STEP 09 frozen UI cannot be silently redesigned.

## Required manual I12-01 acceptance before I12-02B
On the Windows artifact:
1. open Profil Google;
2. create a user-owned local profile;
3. click Buka / Fokuskan Sesi Login;
4. manually complete Google login/MFA/CAPTCHA;
5. return and click Cek Ulang Sesi;
6. confirm status Siap;
7. close the app fully;
8. reopen and confirm the same profile remains and can still report Siap if Google kept the session.

Never share password, MFA code, cookies, browser profile/session files, or tokens.

## Next exact action
Do not implement the live Google Flow driver yet.
After I12-01 real-account validation succeeds and the product owner explicitly says **“lanjutkan”**, begin I12-02B with one Scene only. The first live driver must retain the I12-02A one-submit/ambiguous-outcome rules and must not mix result downloading or Gemini into the same slice.
