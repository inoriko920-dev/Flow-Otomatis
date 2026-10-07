# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Factory STEP active: STEP 12 — Integrations & External Services
- STEP 12 status: IN PROGRESS
- I12-01 — Authorized Google Session / Manual Login Lifecycle: AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING
- Last tested implementation SHA: 70dd90b7e08c0f0b9261021a4f02966daf046c60
- Final I12-01 automated CI run: 37602579445 — SUCCESS
- Quality job: 112730274502 — SUCCESS
- UI regression job: 112730670338 — SUCCESS
- Windows package job: 112730961256 — SUCCESS
- UI regression artifact ID: 11473523196
- UI regression artifact digest: sha256:fa5ab49c244259108cd6ae06dcc69ad076bd9cce748a36662e6c3172e9d9f3ff
- Windows portable artifact ID: 11473218426
- Windows portable artifact uploaded size: 435450690 bytes
- Windows portable artifact digest: sha256:21cf2df1f869e31b5632e3cf8320cd08f3fcc50c5ca5088f226f220cdb4c6338
- Live Google login/session persistence against a real account: NOT YET VALIDATED
- Live Google Flow generation/download and Gemini provider: NOT TESTED

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
  - I12-02: BLOCKED until I12-01 live manual validation is accepted
  - I12-03: PLANNED after I12-02
  - I12-04: PLANNED after I12-03

## I12-01 delivered implementation
- Application-owned `GoogleSessionPort`, credential-free `GoogleSessionProfile`, and explicit states:
  - READY
  - NEEDS_LOGIN
  - UNKNOWN
  - ERROR
- `GoogleSessionService` validates user-owned local profile labels and owns application orchestration.
- Dedicated Playwright Browser Worker owns all real browser/session behavior.
- Official Google login surface opens at `https://accounts.google.com/`.
- Session readiness probe navigates to `https://myaccount.google.com/` and maps only sanitized state/detail back to the app.
- Persistent browser profile data is isolated under the user-scoped Session root:
  - `%LOCALAPPDATA%/Flow-Otomatis/Sessions/google/<profile-id>/browser-data`
- Safe local metadata is stored separately in `profile.json`.
- Metadata contains only:
  - profile_id
  - label
  - state
  - last_checked_at
  - detail
- Passwords, MFA values, cookies, auth tokens, credentials, and browser storage are never copied into project DB, result manifests, logs, planning docs, or handoff manifests.
- Profil Google UI now renders real local profiles/status instead of only a fixture.
- Bantuan Login UI now supports:
  - create named local profile;
  - open/focus official login session;
  - manual password/MFA/CAPTCHA handoff;
  - check one profile;
  - check all profiles;
  - Ready / Needs Login / Unknown / Error feedback.
- Browser contexts are closed on application shutdown.
- Profile-scoped cancel closes the browser context without deleting the persisted session.
- Profile delete removes only that app-local session/profile directory.
- No generation submit, result detection/download, Gemini call, CAPTCHA bypass, MFA bypass, hidden rotation, or credential export was added in I12-01.

## I12-01 automated evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 55 source files.
- architecture guard: PASS.
- pytest: 46 passed.
- Frozen UI regression: 30/30 PASS.
- Visual similarity range: 0.6344–0.9643 at threshold 0.55.
- Playwright Chromium staging/smoke: PASS.
- PyInstaller onedir build: PASS.
- Portable application smoke: PASS.
- I12-01 Windows artifact: `Flow-Otomatis-step12-i12-01-win-x64`.
- I12-01 UI evidence artifact: `Flow-Otomatis-step12-i12-01-ui-regression-evidence`.

## Architecture/product rules still frozen
- CPython 3.14.x x64 + PySide6 Qt Widgets.
- Playwright Chromium belongs to the dedicated Browser Worker/provider boundary.
- Presentation must not import Playwright/workers/infrastructure directly.
- Modular monolith + ports/adapters.
- SQLite per-project persistence.
- Windows Credential Locker/keyring remains canonical for API secrets.
- Browser session data belongs only to the user-scoped Session root.
- PyInstaller onedir portable ZIP.
- Serial R1 generation queue.
- Omni Flash 1.1 • 720p • 16:9.
- Audio/SRT Target is authoritative.
- Flow duration values are 4/6/8/10.
- Generate and Download remain separate states.
- No CAPTCHA/MFA bypass.
- No credential/session export.
- No hidden account/key rotation or quota/rate-limit evasion.
- STEP 09 frozen UI cannot be silently redesigned.

## Known limitations / manual validation required
I12-01 automated evidence proves architecture, persistence paths, state contracts, fixture transitions, UI binding, packaged Chromium availability, and portable startup. It does **not** prove a real Google account will accept and retain a live session on the user's machine.

Before I12-02 is accepted to start, manually validate the Windows artifact:
1. launch Flow-Otomatis;
2. open Profil Google;
3. create a profile;
4. choose Buka / Fokuskan Sesi Login;
5. complete Google password/MFA/CAPTCHA manually;
6. return to the app and choose Cek Ulang Sesi;
7. verify status becomes Siap;
8. close Flow-Otomatis completely;
9. reopen it and verify the same profile remains available and can still report Siap where Google's session remains valid;
10. optionally sign out/expire the session and verify it returns to Perlu Login/attention without bypass.

Do not record or share passwords, MFA codes, cookies, browser profile files, or session tokens as validation evidence.

## Remaining STEP 12 order
1. **I12-01 — Authorized Google Session / Manual Login Lifecycle**
   - implementation + automated gates: PASS;
   - live manual validation: PENDING.
2. **I12-02 — Deterministic Google Flow Generation Adapter**
   - one Scene first;
   - Browser Worker boundary;
   - map existing GenerationRequest to real Flow UI;
   - timeout/cancel/idempotency;
   - no duplicate submit after ambiguous outcome.
3. **I12-03 — Live Result Detection & Download Adapter**
   - detect completed result;
   - download to explicit local output;
   - verify file before marking DOWNLOADED;
   - preserve Generate/Download separation.
4. **I12-04 — Gemini AI Agent / Key Integration**
   - keyring-backed secrets;
   - masked UI;
   - bounded context/tool permissions;
   - no automatic key/account rotation to evade limits.

## Next exact action
Do not start I12-02 yet.
The product owner should test the I12-01 Windows artifact with a real user-owned Google account and report the result. After successful manual validation and the next explicit **“lanjutkan”**, mark I12-01 fully PASS and begin I12-02 only.
