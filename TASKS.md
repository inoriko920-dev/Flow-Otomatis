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
- Status: AUTOMATED PASS + SYSTEM CHROME AUTH FIX READY / LIVE REAL-ACCOUNT VALIDATION PENDING.
- Real Google account login/restart persistence still requires product-owner validation.
- Safe restart-proof support is now implemented:
  - first READY records sanitized app-instance/timestamp evidence;
  - READY from the same instance does not pass;
  - READY from a later app instance records restart verification;
  - gate requires current state to remain READY;
  - no credentials/session contents are stored.
- Tested SHA: `0e6b8e3755721954a0d2be8d712f0af88e961e4a`.
- CI: `37615288655` — SUCCESS.
- Quality: `112772031746` — SUCCESS.
- UI visual: `112772307027` — SUCCESS.
- Windows package: `112772535490` — SUCCESS.
- pytest: 79 passed.
- UI artifact: `11479174307`.
- Previous Windows artifact: `11479739543`.
- Restart-gate UI is now explicit on Bantuan Login:
  - `Restart belum diverifikasi` + `Validasi restart: Belum lulus`;
  - `Restart berhasil diverifikasi` + `Validasi restart: Lulus`.
- Latest tested SHA: `5cb889e20a4300b1fa5ae215986239e556b9b553`.
- Latest CI: `37616109456` — SUCCESS.
- Latest quality: `112774708163` — SUCCESS.
- Latest UI visual: `112774969887` — SUCCESS.
- Latest Windows package: `112775342322` — SUCCESS.
- Latest pytest: 80 passed.
- Latest UI artifact: `11480590257`.
- Previous Windows artifact: `11480900497`.
- System-Chrome auth fix:
  - manual authentication now opens installed Google Chrome in normal mode;
  - no Playwright/CDP is attached during Google sign-in;
  - after successful login the user closes the login Chrome window;
  - Cek Ulang Sesi then relaunches the same isolated profile with localhost CDP and attaches Playwright;
  - no stealth/bypass/session export.
- Latest tested SHA: `cbfaa368fd051e0d0a648643bba0fa76484b7d8d`.
- Latest CI: `37633516723` — SUCCESS.
- Latest quality: `112833623396` — SUCCESS.
- Latest UI visual: `112834024070` — SUCCESS.
- Latest Windows package: `112834514993` — SUCCESS.
- Latest pytest: 90 passed.
- Latest mypy: 63 source files.
- Latest UI artifact: `11487353178`.
- Latest Windows artifact: `11486833906`.
- Real-account acceptance and restart persistence remain PENDING local validation.

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

### I12-02B2-GATE — Restart-Gated Generation Provider Contract
- Status: PASS.
- Tested implementation SHA: `6abfbc169a0864c00f1136cfc7dd6a7fe7583b8a`.
- CI: `37617108389` — SUCCESS.
- Quality: `112778002338` — SUCCESS.
- UI visual: `112778281237` — SUCCESS.
- Windows package: `112778575235` — SUCCESS.
- pytest: 85 passed.
- mypy: 62 source files.
- UI artifact: `11480692141`.
- Windows artifact: `11481001812`.
- Blocks downstream generation when restart validation is not currently valid.
- Blocked path makes zero downstream provider calls.
- Passed gate forwards one request.
- Runtime live provider is not yet composed; future I12-02B2-LIVE wiring must use this wrapper.

### I12-02B2-LIVE — Live One-Scene Google Flow Submit Driver
- Status: BLOCKED pending successful I12-01 real-account validation.
- Start only after successful manual validation + next explicit `lanjutkan`.
- Use current verified authorized Flow UI only.
- Exactly one mutating attempt.
- No silent retry.
- Ambiguous outcome → ATTENTION_REQUIRED.
- No result download in this slice.

### I12-03A — Safe Generated-Media Download Foundation
- Status: PASS / PRE-LIVE FOUNDATION COMPLETE.
- Main implementation: `d71ddc73de8444a0811d8bfdd3066e72e704565f`.
- Provider-neutral Download contract is separate from Generate.
- Download requires confirmed `GENERATED` state + stable `remote_result_id`.
- Canonical project output uses `.part` then atomic publish.
- Existing files are never overwritten silently.
- AUTH_REQUIRED / CANCELLED / AMBIGUOUS / SAFE_FAILURE are typed; no silent retry.
- Synthetic regression proves success, idempotence, collision protection, and failure persistence.
- Live Flow result discovery/download selectors remain intentionally unimplemented until authorized live UI is inspected.

### I12-03-LIVE — Live Result Detection & Download Driver
- Status: BLOCKED behind I12-02B2-LIVE.
- Start only after one-Scene live Generate is accepted and a stable remote result identity is proven.
- Reuse I12-03A service/provider contracts; do not redesign Download lifecycle.
- No guessed selectors and no silent retry.

### I12-04A — Secure Gemini Key Integration
- Status: PASS / PRE-LIVE FOUNDATION COMPLETE.
- Main implementation: `997b93384188648a848560b249cd35e410c07bf2`.
- Up to 100 user-owned keys may be imported; duplicates are fingerprinted/skipped.
- Raw keys are stored in OS keyring, never project SQLite/export/UI.
- SQLite stores only masked/fingerprinted metadata and explicit active selection.
- Health check uses the official Gemini models endpoint with `x-goog-api-key`.
- Key selection is manual; health/rate-limit events never rotate keys automatically.
- Real-key health validation is user-owned input and can be tested locally from the final build.

### I12-04B — Read-Only Gemini AI Agent
- Status: PASS.
- Main implementation: `8246d194a56cfdbf3c2818a570dc637a37633891`.
- Agent reads bounded project/Scene context and returns text guidance only.
- Default model: `gemini-3.8-flash`.
- No tools/function calling; no Generate/Download/login/retry/key-switch action can be executed by the Agent.
- API key is sent only via `x-goog-api-key`; it is not embedded in URL/prompt/body.
- Rate-limit failure performs exactly one request and never auto-switches key/model.
- Qt Agent call runs off the UI thread; heartbeat regression PASS.
- Official main CI `37664172842`: 128 tests PASS, mypy 80 source files, architecture PASS, frozen UI 30/30 PASS, Chromium/portable smoke PASS.
- Latest Windows artifact: `11502048305`, 435713508 bytes, SHA-256 `631ab49ed5f7a3f7c99f9df496fd8109625efa25288bf5e7bc66c2865c6c69ed`.

### STEP 12 current product gate
- PRE-LIVE READY.
- All safe/offline foundations that do not require the product owner's real Google/Flow session are complete.
- Required manual gate before live mutation: I12-01 real-account login + READY-after-restart validation.
- After that: I12-02B2-LIVE one Scene only → I12-03-LIVE result detection/download.


## STEP 12 safety boundary
- No CAPTCHA/MFA bypass.
- No credential/session export.
- No automatic account/key rotation to evade limits.
- No guessed live generation selectors.
- No silent retry after ambiguous mutation.

### STEP 12 Audit Remediation — A00–A05
- A00 — Source-of-truth synchronization and baseline verification: PASS.
  - audit DOCX committed under `docs/planning/audits/`;
  - cross-layer decisions recorded as ADR-015/016/017;
  - official Windows Python 3.14.7 + uv 0.12.23 quality job SUCCESS;
  - 90 tests passed; mypy 63 source files; architecture guard PASS.
- A01 — F01 + F02 import/data linkage: PASS.
  - merge SHA: `865e92f4a3da01a35339203f263ab938a420d3bd`;
  - missing prompt TXT now fails with typed `PROMPT_FILE_MISSING` before persistence;
  - duplicate create is rejected atomically and preserves prior jobs/downloads;
  - official main CI `37644208386`: 95 tests PASS, mypy/architecture PASS, UI 30/30 PASS, Windows portable smoke PASS.
- A02 — F04 corrupt-data isolation: PASS.
  - merge SHA: `9525a9d8ed370ab8b3f3ed916735e03ef04ecfce`;
  - canonical SQLite reads are read-only and typed corrupt-data errors isolate bad projects;
  - healthy projects remain listable/openable while corrupt entries are surfaced safely;
  - source DB non-mutation is regression-tested by SHA-256;
  - official main CI `37647427626`: 99 tests PASS, mypy/architecture PASS, UI 30/30 PASS, Windows portable smoke PASS.
- A03 — F03 + F06 request revision/lease/recovery: PASS.
  - merge SHA: `3ee8d8118c1a137ac5c24d6ed7896b15bb3ccafb`;
  - coherent request snapshot/fingerprint is verified before dispatch;
  - durable owner/lease recovery blocks blind resubmit;
  - versioned migration preserves confirmed results/download linkage;
  - main CI `37651619177`: 106 tests PASS, mypy/architecture PASS, UI 30/30 PASS, Windows portable smoke PASS.
- A04 — F05 Browser Worker/UI responsiveness: PASS.
  - merge SHA: `837106d5e83839150706dfdf3857734308258184`;
  - browser-touching session work now runs through one dedicated single-thread Browser Worker command owner;
  - Qt uses async Future → Qt Signal delivery and receives sanitized DTO/status/error values only;
  - duplicate same-profile operations are blocked while busy and shutdown waits are bounded;
  - slow-probe Qt heartbeat regression PASS;
  - official main CI `37654708047`: 110 tests PASS, mypy 64 source files, architecture PASS, UI 30/30 PASS, Chromium/portable smoke PASS.
- A05 — combined verification/build/handoff: PASS.
  - fresh tested SHA: `7c1545c775fede2442a89d54d828e32813b9c8a5`;
  - acceptance matrix T01–T12 PASS;
  - official fresh CI `37656131625`: 110 tests PASS, mypy 64 source files, architecture PASS, UI 30/30 PASS, Chromium/portable smoke PASS;
  - audit findings F01–F06 CLOSED;
  - audit remediation A00–A05 COMPLETE.
- Next product gate is not another audit package: manual real-account Google login/restart validation remains required before I12-02B2-LIVE.

Audit remediation does not unblock I12-02B2-LIVE. Live Generate remains gated by the existing real-account restart validation.

