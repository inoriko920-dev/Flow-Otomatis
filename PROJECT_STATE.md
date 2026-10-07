# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Factory STEP active: STEP 12 — Integrations & External Services
- STEP 12 status: IN PROGRESS
- I12-01 — Authorized Google Session / Manual Login Lifecycle: AUTOMATED PASS + SYSTEM CHROME AUTH FIX READY / LIVE REAL-ACCOUNT VALIDATION PENDING
- I12-02A — Deterministic Submit Contract & Ambiguous-Submit Guard: PASS
- I12-02B1 — Read-Only Google Flow Preflight: PASS
- I12-02B2-PRECHECK — Pre-Submit Request Guard: PASS
- I12-02B2-GATE — Restart-Gated Generation Provider Contract: PASS
- I12-02B2-LIVE — Live One-Scene Google Flow Submit Driver: BLOCKED pending real-account session validation
- Last tested implementation SHA: cbfaa368fd051e0d0a648643bba0fa76484b7d8d
- I12-01-SYSTEM-CHROME-AUTH CI run: 37633516723 — SUCCESS
- Quality job: 112833623396 — SUCCESS
- UI regression job: 112834024070 — SUCCESS
- Windows package job: 112834514993 — SUCCESS
- pytest: 90 passed
- mypy strict: 63 source files
- UI evidence artifact ID: 11487353178
- UI evidence digest: sha256:cae786100222df13c8da3dfd0c36ba86390b40ff211ee8b6473b9596f974328d
- Windows artifact ID: 11486833906
- Windows artifact size: 435478667 bytes
- Windows artifact digest: sha256:d99e356615899f2eb9d5f99a3d1b8f37e315e3857cd14990acd432acc3c6baca
- Previous I12-02B2-GATE CI run: 37617108389 — SUCCESS
- Quality job: 112778002338 — SUCCESS
- UI regression job: 112778281237 — SUCCESS
- Windows package job: 112778575235 — SUCCESS
- pytest: 85 passed
- mypy strict: 62 source files
- UI evidence artifact ID: 11480692141
- UI evidence digest: sha256:b7ec06b0ec28fe330c8dae6467efd963ef353e538bccf5ca4ee6be740c725bc6
- Windows artifact ID: 11481001812
- Windows artifact size: 435469955 bytes
- Windows artifact digest: sha256:e24ff70fb31cc8ffa31de2fa1f6af5507f742d6ace49bf77d5ad548e1dd19d75
- Previous I12-01-RESTART-PROOF-UI CI run: 37616109456 — SUCCESS
- Quality job: 112774708163 — SUCCESS
- UI regression job: 112774969887 — SUCCESS
- Windows package job: 112775342322 — SUCCESS
- UI evidence artifact ID: 11480590257
- UI evidence digest: sha256:7b6c4ce3d7dd4ea8048bdd8ade8deb0a3c079cedbf57d057c867be65f775f0bf
- Windows artifact ID: 11480900497
- Windows artifact size: 435468948 bytes
- Windows artifact digest: sha256:cfbb320859360b877f3362684915cc32db1e11aa33ce39d8421f5a2e3b631b4a
- Previous I12-01-RESTART-PROOF CI run: 37615288655 — SUCCESS
- Quality job: 112772031746 — SUCCESS
- UI regression job: 112772307027 — SUCCESS
- Windows package job: 112772535490 — SUCCESS
- UI evidence artifact ID: 11479174307
- UI evidence digest: sha256:5c92598d30204c77723c07ad66faa1673f24d27092eceb040c56768123709245
- Windows artifact ID: 11479739543
- Windows artifact size: 435467636 bytes
- Windows artifact digest: sha256:736b3a7b95ece7dd64a0516f0b147934050bf8ba61b6ae2957e9eef073f56107
- Previous I12-02B2-PRECHECK CI run: 37605969763 — SUCCESS
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
  - I12-01: AUTOMATED PASS + SYSTEM CHROME AUTH FIX READY / LIVE REAL-ACCOUNT VALIDATION PENDING
  - I12-02A: PASS
  - I12-02B1: PASS
  - I12-02B2-PRECHECK: PASS
  - I12-02B2-GATE: PASS
  - I12-02B2-LIVE: BLOCKED pending I12-01 live validation
  - I12-03: PLANNED after live generation submit
  - I12-04: PLANNED after I12-03

## I12-01-SYSTEM-CHROME-AUTH fix delivered
The previous login path opened Google sign-in inside Playwright-controlled Chromium and produced Google's "This browser or app may not be secure" rejection on the product owner's Windows machine.

Replacement architecture:
- manual Google sign-in opens the installed Google Chrome executable, not bundled Playwright Chromium;
- manual sign-in uses the app-owned isolated `browser-data` directory;
- manual sign-in has no Playwright attachment, no CDP endpoint, and no automation/stealth flags;
- the user completes password/MFA/CAPTCHA manually and then closes the login Chrome window;
- only after login is finished does `Cek Ulang Sesi` relaunch the same isolated profile with a random localhost CDP endpoint;
- Playwright attaches through `connect_over_cdp` only after authentication for authorization checks and later Flow work;
- passwords, MFA values, cookies, tokens, and browser profile contents are never exported through the application contract;
- there is no stealth driver, CAPTCHA bypass, or anti-detection patch.

Automated evidence:
- Ruff format/lint: PASS;
- mypy strict: PASS — 63 source files;
- architecture guard: PASS;
- pytest: 90 passed;
- frozen UI regression: 30/30 PASS;
- visual similarity: 0.6344–0.9643;
- staged Chromium smoke: PASS;
- PyInstaller onedir build: PASS;
- portable smoke: PASS.

Important boundary:
- CI proves the implementation/build contract only;
- CI cannot authenticate the product owner's real Google account;
- the Windows build must still be tested locally to confirm Google accepts the normal-Chrome login and retains the session;
- I12-02B2-LIVE remains blocked until local READY-after-restart validation passes.

## I12-02B2-GATE delivered
This safe slice adds an application-layer `RestartGatedGenerationProvider` that must sit in front of any future live generation provider.

Delivered:
- generation is refused with `GenerationAuthenticationRequiredError` when the selected profile has not passed READY-after-restart;
- READY without cross-instance restart proof is blocked;
- NEEDS_LOGIN, UNKNOWN, and ERROR remain blocked even if restart proof existed earlier;
- blocked requests never call the downstream provider;
- a passed restart gate forwards exactly one request to downstream;
- the queue already maps `GenerationAuthenticationRequiredError` to ATTENTION_REQUIRED, preserving the anti-retry safety contract;
- no Flow selector, upload, prompt entry, settings mutation, project mutation, or Generate click was added.

Automated evidence:
- Ruff format/lint: PASS;
- mypy strict: PASS — 62 source files;
- architecture guard: PASS;
- pytest: 85 passed;
- frozen UI regression: 30/30 PASS;
- visual similarity: 0.6344–0.9643;
- Chromium staging/smoke: PASS;
- PyInstaller onedir build: PASS;
- portable smoke: PASS.

Critical composition note:
- the live Google Flow generation provider is not yet wired into `bootstrap/main.py`;
- therefore this guard is a verified contract ready for mandatory live wiring, not proof that real Generate is operational;
- when I12-02B2-LIVE is implemented, the live provider must be wrapped by `RestartGatedGenerationProvider`; direct ungated runtime wiring is forbidden.

## I12-01-RESTART-PROOF UI delivered
The existing credential-free restart proof is now visible to the product owner on the real Google login surface.

Delivered:
- Bantuan Login reads `GoogleSessionRestartGate` through the application service;
- READY + no cross-instance proof shows `Restart belum diverifikasi`;
- READY + verified restart shows `Restart berhasil diverifikasi`;
- the safe-status card shows `Validasi restart: Lulus / Belum lulus`;
- instructions explicitly say to close the app, reopen it, and run Cek Ulang Sesi again;
- UI tests cover both not-yet-verified and verified states;
- no Flow generation mutation was added.

Automated evidence:
- Ruff format/lint: PASS;
- mypy strict: PASS — 61 source files;
- architecture guard: PASS;
- pytest: 80 passed;
- frozen UI regression: 30/30 PASS;
- visual similarity: 0.6344–0.9643;
- Chromium staging/smoke: PASS;
- PyInstaller onedir build: PASS;
- portable smoke: PASS.

The live real-account gate remains pending because CI cannot authenticate the product owner's account.

## I12-01-RESTART-PROOF hardening delivered
This safe slice strengthens the manual gate without performing any Google Flow mutation.

Delivered:
- new `GoogleSessionRestartGate` application contract;
- `GoogleSessionService.get_restart_gate(...)`;
- Browser Worker stores a sanitized `restart-proof.json` beside the local profile metadata;
- first READY observation records only a random app-instance id and timestamp;
- READY on the same app instance does not satisfy the restart gate;
- READY observed by a later app instance records `restart_verified_at`;
- `ready_after_restart` is true only when restart proof exists and the current profile state is still READY;
- if the session later becomes NEEDS_LOGIN, the gate immediately evaluates false;
- no password, cookie, token, credential, browser-data, URL query, or session contents are stored in the restart proof;
- no Flow selector, upload, prompt entry, settings mutation, or Generate click was added.

Automated evidence:
- Ruff format/lint: PASS;
- mypy strict: PASS — 61 source files;
- architecture guard: PASS;
- pytest: 79 passed;
- frozen UI regression: 30/30 PASS;
- visual similarity: 0.6344–0.9643;
- Chromium staging/smoke: PASS;
- PyInstaller onedir build: PASS;
- portable smoke: PASS.

Important: this makes the local restart check machine-verifiable after the user runs it, but CI still cannot authenticate the product owner's real Google account. Therefore the live gate remains pending until a real local profile produces READY before and after an actual app restart.

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
Using the latest Windows artifact:
1. open Profil Google;
2. create/open a user-owned profile;
3. choose Buka / Fokuskan Sesi Login;
4. complete Google login manually in the normal installed Google Chrome window;
5. after login succeeds, fully close that Chrome login window;
6. return to Flow-Otomatis and choose Cek Ulang Sesi; it must report Siap;
7. fully close Flow-Otomatis;
8. reopen Flow-Otomatis;
9. check the same profile again and confirm Validasi restart: Lulus.

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

## STEP 12 audit remediation track — A00
- A00 status: PASS.
- ASTRA audit source: `docs/planning/audits/00_ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-07.docx`.
- Original uploaded audit SHA-256: `1011693e1e67673a4af49378ca2009e93f596a74f563276ae060ebcaae0ca210` (48486 bytes).
- Repository compact text-equivalent audit SHA-256: `39ee9d8c37aa573f019649b7f6f04c76812e80cf88b397e5694e0c96f9946527` (10028 bytes); full logical text preserved, formatting simplified, render verification PASS.
- ASTRA baseline SHA: `e6724a0a5c3d68789149ed5c7eb094d44c9f0967`.
- A00 documentation-sync commit: `bc550e57407d1be09fceb64eadd18217f4d9c37c`.
- Official CI run: `37639865121`.
- Quality job: `112855631708` — SUCCESS.
- Runtime: Windows Server 2025, CPython 3.14.7 x64, uv 0.12.23.
- `uv sync --frozen --all-groups`: PASS.
- `uv run ruff format --check .`: PASS — 123 files already formatted.
- `uv run ruff check .`: PASS.
- `uv run mypy src/flow_otomatis`: PASS — 63 source files.
- `uv run python scripts/check_architecture.py`: PASS.
- `uv run pytest -q tests/unit tests/contract tests/integration tests/smoke tests/ui`: PASS — 90 passed, 1827 warnings.
- Compare `e6724a0...` → `bc550e5...` contains documentation only; no source/test/runtime code changed, so F01–F06 remain applicable.
- ADR-015, ADR-016, and ADR-017 are accepted as implementation boundaries for A01, A03, and A04.
- I12-02B2-LIVE remains BLOCKED; A00 does not authorize live Generate.

### Audit next exact action
After the product owner says `lanjutkan`, execute only A01: close F01 and F02 with atomic create semantics, missing-prompt typed validation, regression tests, and no destructive project replacement.

## STEP 12 audit remediation track — A01
- A01 status: PASS.
- Findings closed: F01 and F02.
- Implementation merge SHA: `865e92f4a3da01a35339203f263ab938a420d3bd`.
- PR: #1 — `A01: fix import integrity and atomic workspace creation`.
- PR head SHA: `2aa9de28ce0ba379d3ed11b1ba1d6a035d5b01a4`.
- Official main CI run: `37644208386` — SUCCESS.
- Quality job: `112870617392` — SUCCESS.
- UI visual job: `112871584570` — SUCCESS.
- Windows package job: `112872148801` — SUCCESS.
- Runtime: Windows Server 2025, CPython 3.14.7 x64, uv 0.12.23.
- Ruff format: PASS — 125 files already formatted.
- Ruff lint: PASS.
- mypy: PASS — 63 source files.
- architecture guard: PASS.
- pytest: PASS — 95 passed, 1827 warnings.
- frozen UI regression: PASS — 30/30 fixtures, similarity 0.6344–0.9643.
- UI evidence artifact: `11493692056`, SHA-256 `b0e8d1671e0e368b21a09a31595e9502efd9e0efe8e6ce61db89539bc645a200`.
- Playwright Chromium smoke: PASS.
- portable application smoke: PASS.
- Windows artifact: `11494735790`, 435479977 bytes, SHA-256 `8a17a7f24aaa203877326952fe97f3b711c40ceac3a603fd3310b76b5c0990a9`.

### A01 delivered
- ZIP/folder prompt values ending in `.txt` are treated as file references; missing files raise typed `PackageValidationError(code="PROMPT_FILE_MISSING")` before workspace persistence.
- Missing-prompt errors identify the Scene and safe relative reference.
- `WorkspaceRepositoryPort` now exposes explicit `create` and `update` semantics.
- imports use atomic `create`; duplicate episode identity is rejected under `BEGIN IMMEDIATE` with `WorkspaceAlreadyExistsError`.
- Scene planning uses the explicit update path.
- duplicate import does not delete/reset prior project state, generation jobs, or download results.
- Qt create action translates duplicate identity into a safe Indonesian message and directs the user to the existing project.
- regression coverage proves missing TXT ZIP/folder rejection, empty/UTF-8 prompt handling, old duration/traversal behavior, prior job/download preservation, and concurrent duplicate creation safety.

### Findings still open after A01
- F03 — queued request revision/readiness consistency.
- F04 — corrupt scene data can break project listing.
- F05 — Google session probing can block the Qt UI thread.
- F06 — orphan RUNNING job recovery is incomplete.

I12-02B2-LIVE remains BLOCKED by the existing real-account restart validation gate; A01 does not authorize live Generate.

### Audit next exact action
After the product owner says `lanjutkan`, execute only A02 for F04: isolate corrupt project data at the canonical SQLite read boundary, keep healthy projects usable, surface corruption safely in Project Hub, never mutate the corrupt source while reading, and stop before A03.

## STEP 12 audit remediation track — A02
- A02 status: PASS.
- Finding closed: F04.
- Implementation merge SHA: `9525a9d8ed370ab8b3f3ed916735e03ef04ecfce`.
- PR: #2 — `A02: isolate corrupt workspace data`.
- Final PR head: `989a57dc026f9544334803711c99544caad1044e`.
- Official main CI run: `37647427626` — SUCCESS.
- Quality job: `112881739521` — SUCCESS.
- UI visual job: `112882633481` — SUCCESS.
- Windows package job: `112883036794` — SUCCESS.
- Ruff format: PASS — 127 files already formatted.
- Ruff lint: PASS.
- mypy: PASS — 63 source files.
- architecture guard: PASS.
- pytest: PASS — 99 passed, 1904 warnings.
- frozen UI regression: PASS — 30/30 fixtures, similarity 0.6344–0.9643.
- UI evidence artifact: `11494409352`, 3316911 bytes, SHA-256 `3a213c84085d22340b5bdc7f0bd8882ffeeff6becf5c8416ecef0c06fb01c20f`.
- Playwright Chromium smoke: PASS.
- portable application smoke: PASS.
- Windows artifact: `11495321054`, 435481873 bytes, SHA-256 `fa9bd2be4725cc1af42d84b09755d2ca5f3f1862125c7cef98ab847d2684181e`.

### A02 delivered
- canonical workspace reads now use SQLite read-only mode and never create/repair schema while inspecting an existing project;
- invalid readiness enum, numeric conversion, timestamp conversion, and corrupt SQLite data are normalized to typed storage/corruption errors rather than leaking raw decode exceptions;
- `scan_recent` returns healthy workspaces plus isolated `CORRUPT` / `UNAVAILABLE` entries;
- one corrupt project no longer prevents healthy projects from appearing or opening;
- Project Hub reuses the frozen five-column layout and marks damaged entries honestly as `Data Rusak` / `Tidak Tersedia`;
- opening a corrupt/unavailable entry from Qt is translated into a safe Indonesian warning;
- regression tests hash the corrupt SQLite file before/after listing/open attempts and prove read/recovery discovery does not modify the source database.

### Findings still open after A02
- F03 — queued request revision/readiness consistency.
- F05 — Google session probing can block the Qt UI thread.
- F06 — orphan RUNNING job recovery is incomplete.

I12-02B2-LIVE remains BLOCKED by the existing real-account restart validation gate. A02 does not authorize live Generate.

### Audit next exact action
After the product owner says `lanjutkan`, execute only A03 for F03 and F06 under ADR-016: request revision/fingerprint consistency plus owner/lease recovery, transactional migration, zero blind resubmit, full local queue/results regressions, then stop before A04.

