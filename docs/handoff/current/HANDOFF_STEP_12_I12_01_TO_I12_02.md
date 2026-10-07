# HANDOFF — STEP 12 / I12-01 → I12-02

## Gate
I12-01 — Authorized Google Session / Manual Login Lifecycle:
**AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING**

STEP 12 remains **IN PROGRESS**.

## Project / tested baseline
- Project: Flow-Otomatis
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- Last tested implementation SHA: `70dd90b7e08c0f0b9261021a4f02966daf046c60`
- CI run: `37602579445` — SUCCESS
- Quality job: `112730274502` — SUCCESS
- UI visual job: `112730670338` — SUCCESS
- Windows package job: `112730961256` — SUCCESS

## I12-01 delivered
- Application contract:
  - `application/ports/google_session.py`
  - `GoogleSessionState`
  - `GoogleSessionProfile`
  - `GoogleSessionPort`
- Application orchestration:
  - `application/services/google_sessions.py`
- Browser/session adapter:
  - `workers/browser/google_session_worker.py`
  - persistent Playwright context per local profile;
  - official accounts.google.com manual login;
  - myaccount.google.com readiness probe;
  - sanitized state only leaves Browser Worker.
- Runtime presentation:
  - `presentation/google_profiles_view.py`
  - `MainWindow` now binds Profil Google/Bantuan Login to real local session state.
- Bootstrap:
  - composes GoogleSessionService + GoogleSessionWorker with PathService session/browser roots.
- Tests:
  - integration fixture verifies safe persisted metadata and profile-scoped cancel/delete;
  - UI fixture verifies profile → login → Ready transition.
- Packaging:
  - packaged Chromium is staged and smoke-tested;
  - portable app smoke passes.

## Session storage boundary
Allowed:
- `%LOCALAPPDATA%/Flow-Otomatis/Sessions/google/<profile-id>/profile.json`
- `%LOCALAPPDATA%/Flow-Otomatis/Sessions/google/<profile-id>/browser-data/`

The safe metadata file contains only:
- profile_id
- label
- state
- last_checked_at
- detail

Forbidden outside browser-data:
- password;
- MFA code;
- cookies;
- auth/session tokens;
- credential exports;
- copied browser storage.

Do not put session/browser data into:
- project SQLite;
- FLOW_OTOMATIS_RESULT.json;
- logs;
- screenshots/evidence;
- planning/handoff documents;
- Git.

## Automated evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 55 source files.
- architecture guard: PASS.
- pytest: **46 passed**.
- Frozen visual regression: **30/30 PASS**.
- Similarity: **0.6344–0.9643**, threshold 0.55.
- Chromium staging/smoke: PASS.
- PyInstaller onedir: PASS.
- Portable smoke: PASS.

Artifacts:
- UI regression: `Flow-Otomatis-step12-i12-01-ui-regression-evidence`
  - ID: `11473523196`
  - size: `3316911` bytes
  - digest: `sha256:fa5ab49c244259108cd6ae06dcc69ad076bd9cce748a36662e6c3172e9d9f3ff`
- Windows package: `Flow-Otomatis-step12-i12-01-win-x64`
  - ID: `11473218426`
  - size: `435450690` bytes
  - digest: `sha256:21cf2df1f869e31b5632e3cf8320cd08f3fcc50c5ca5088f226f220cdb4c6338`

## What is NOT proven
Do not claim these are ready yet:
- successful login against the product owner's real Google account;
- real Google session persistence after packaged-app restart;
- real expired/logout transition;
- Google Flow page automation;
- live generation submit;
- live result detection/download;
- Gemini integration;
- live network/rate-limit/provider error mapping.

## Required manual I12-01 acceptance
On the Windows artifact:
1. open Profil Google;
2. create a user-owned local profile;
3. click Buka / Fokuskan Sesi Login;
4. manually complete Google login/MFA/CAPTCHA;
5. return and click Cek Ulang Sesi;
6. confirm status Siap;
7. close the app fully;
8. reopen and confirm the same profile remains and can still report Siap if Google kept the session;
9. sign out/expire if practical and verify Needs Login/attention appears without bypass.

Never send passwords, MFA codes, cookies, session files, or tokens back as evidence. A screenshot of the app's sanitized status is sufficient if troubleshooting is needed.

## Next integration after manual acceptance
### I12-02 — Deterministic Google Flow Generation Adapter
Start only after:
- manual I12-01 acceptance succeeds; and
- product owner explicitly says **“lanjutkan”**.

First I12-02 slice must remain one Scene only:
- use existing `GenerationRequest`;
- Browser Worker owns Playwright;
- map one request to the real Flow UI;
- define timeout and cancel;
- guard ambiguous submit;
- never silently resubmit if success/failure is unknown;
- do not mix result download or Gemini into the same slice.
