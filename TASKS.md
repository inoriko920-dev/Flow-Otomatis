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

## STEP 12 follow-up ASTRA audit — 8 October 2026
- Baseline reviewed: `0b9e2c4f63a9c0fdab0fe255830964a0e2fb6b39`; no source changes since ASTRA's snapshot.
- R00: documentation sync/source inspection/ADR-018/handoff — PASS on the SOL R00 branch; code untouched.
- B01/P1 health-key selection race: OPEN → R01 T01–T04.
- B02/P2 Gemini Agent stale-context response: OPEN → R01 T05–T08.
- B03/P1 before live missing/changed image after queue prepare: OPEN → R02 T09–T13.
- B06/P2 naive timestamp isolate-and-sort: OPEN → R02 T22–T25.
- B04/P1 missing output still handoff-ready: OPEN → R03 T14–T17.
- B05/P1 before live download publish overwrite: OPEN → R03 T18–T21.
- R04: official combined regression/UI/portable verification after R01–R03; NOT STARTED.
- This follow-up does not undo the prior A00–A05 completion. Live real-account restart gate remains BLOCKED pending owner validation.
- SOL must stop after R00 and wait for explicit permission before R01.

### STEP 12 ASTRA 8 October R01 — CLOSED (B01+B02)
- B01 Gemini health/selection race: CLOSED locally; PATCH-only metadata health writes + request ordering, no activation overwrites/upserts.
- B02 Agent stale-context response: CLOSED locally; immutable request identity, scene/episode/generation gate, window-close safety and per-task signal ownership.
- Tests T01–T08: PASS (deterministic SQLite and Qt regression).
- Code PR #14: https://github.com/inoriko920-dev/Flow-Otomatis/pull/14 (merged).
- Tested code SHA: `9c704e8fee54fd653acdf9f86ac12038d364a8e0`; merged SHA: `eee37612e3a02a1468b49b53a9721d8b0004cc48`.
- Official PR CI `37721917858`: all jobs SUCCESS; 137 tests PASS, Ruff/mypy/architecture PASS; UI frozen 30/30 PASS; Windows Chromium/portable PASS.
- Next package ONLY after explicit user permission: R02 (B03 + B06, T09–T13 and T22–T25).
- B03, B04, B05, B06 remain OPEN; R03/R04 NOT STARTED. Live Google Flow remains BLOCKED.

### STEP 12 follow-up audit R02 — COMPLETE / PASS (8 October 2026)
- B03 P1 missing/modified/unreadable image after queue preparation: CLOSED locally; image byte digest via canonical folder/ZIP reader is bound to prepared request_fingerprint and freshly rechecked before submit_started_at.
- B06 P2 naive timestamps crashing project list: CLOSED locally; timezone-aware boundary for created_at/imported_at, corruption isolated and database not repaired during read.
- Acceptance T09–T13 + T22–T25: PASS with integration SQLite/folder/ZIP and Qt Project Hub coverage; old digestless queued fingerprints are stale until explicit reprepare.
- Implementation PR #15: https://github.com/inoriko920-dev/Flow-Otomatis/pull/15
- Code merge SHA `3a9f445ee9e814a78cd8c7085396f7d4c518259a`; CI-tested SHA `ddf9580bbc3ab2d081c02080892536d416bd2503`, official CI `37723155562`: **153 passed**, Ruff/mypy/architecture PASS, frozen UI 30/30 PASS, Chromium and Windows portable PASS.
- Evidence: `docs/planning/audits/B03_B06_R02_EVIDENCE_2026-10-08.md`.
- Next ONLY after explicit user "lanjutkan": **R03 B04+B05** (local result availability and no-clobber downloads). B04 and B05 OPEN. R04 NOT STARTED. Flow live BLOCKED.

### STEP 12 follow-up — SOL R03 COMPLETE / PASS (8 October 2026)
- B04: CLOSED locally. Real output file readability + nonempty regular-file checks at Hasil snapshot and again in manifest writer; effective UNAVAILABLE blocks editing handoff without deleting historical DownloadRecord.
- B05: CLOSED locally. One unpredictable owned .part per attempt; Windows same-volume atomic os.link no-overwrite publication; collision never clobbers output and retains partial evidence. Losing concurrent FAILED upserts cannot erase successful record. Published final with failed DB save stays untouched and requires explicit manual reconciliation.
- T14–T21 plus supplementary race, compatibility and no-retry cases PASS.
- PR #16 merged to main (`1f82675eb6282a3f5070c4320c5898a4304dd516`), CI tested `17dc2be0c7e4c69a99ab5129ea311492a182ecc4`.
- CI https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37724196252: 165 tests, Ruff/mypy/architecture PASS, frozen UI 30/30 PASS, staged Chromium and Windows portable build/smoke PASS.
- Evidence `docs/planning/audits/B04_B05_R03_EVIDENCE_2026-10-08.md`; ADR-019.
- New ASTRA B01–B06 now CLOSED **locally** in R01–R03, not equivalent to real-account/Flow live acceptance.
- Next step: R04 combined regression + source-hash/artifact audit, NOT STARTED; only after explicit user "lanjutkan".

## 8 October 2026 — SOL R04 FINAL Combined Audit PASS
- R04: **PASS / COMPLETE** for offline/CI-backed verification of new ASTRA findings B01–B06.
- PR #17 https://github.com/inoriko920-dev/Flow-Otomatis/pull/17 merged as `baf3257b293f6b05b4cdbca7e9f3d4aa1272d218`.
- PR gate source `e557a2219350871205d32330c3a0d027bb9e9824`, official CI run `37725045658`: SUCCESS.
- Exact **main tested source SHA** `baf3257b293f6b05b4cdbca7e9f3d4aa1272d218`, main push CI `37725495137`: SUCCESS, all 3 jobs.
- Windows Python 3.14.7 + uv frozen; Ruff format/lint, mypy 81 files, architecture PASS; **192 pytest passed** including T01–T25 explicit audit-inventory tests and existing behavioral tests.
- 30/30 frozen UI, Chromium staged smoke, portable ZIP build, executable portable smoke PASS.
- Main Windows artifact `11527552603` (435,725,819 bytes), sha256 `0ae8a7451acab9c7ed141df0248cb3090831c047ce37f3d14ea00a822942c1dd`, expires 2026-10-22T04:06:30Z.
- Main UI artifact `11527787528` (3,316,911 bytes), sha256 `9092dcc7acf074d496aeb57e6c11a1adb409ba25dc29443dcd585f5c526982dd`, expires 2026-10-22T04:03:15Z.
- Evidence `docs/planning/audits/B01_B06_R04_FINAL_EVIDENCE_2026-10-08.md`; final handoff `docs/handoff/current/HANDOFF_STEP_12_BUG_R04_FINAL_2026-10-08.md`.
- All 6 B01–B06 CLOSED for **offline foundation only**. Historical F01–F06/A00–A05 remain closed.
- **Still BLOCKED:** real user Google login, READY and restart-validation Lulus, I12-02B2-LIVE one-Scene Generate, I12-03-LIVE output download. These were NOT run by R04.
- Caveats: limited CI artifact retention; external strict-enum v1.0 manifest consumers not independently verified for UNAVAILABLE; atomic hardlinks may fail on unsupported filesystems and must fail safely.

## 8 October 2026 — Independent Portable Distribution QA complete
- User confirmed Google **login works**; restart proof `Validasi restart: Lulus` not yet supplied. Live Flow Generate/Download remains BLOCKED.
- Scope approved by user to continue non-login work: strengthen release ZIP verification only, **PASS**.
- PR #18 merged `baff19bb7c28612837d24001b9db9ee4a84251e5`, official main CI `37728080637` SUCCESS: **217 tests**, 30/30 frozen UI, Chromium and Windows portable build/smoke, **real ZIP SHA/CRC/source/path verifier PASS**.
- The new checker caught a real build-order bug: dependency inventory `THIRD_PARTY_NOTICES.txt` used to be generated before cleaning `dist`, causing the distributable ZIP to miss it. Builder now generates the notice after cleaning and requires it.
- ZIP 1,049 files, inner SHA256 `b58bba7b18517f67e6db5a79b299f3bd170a20c5536ab8f11c7d9ed4bfc3a6b2`; source `baff19bb7c28612837d24001b9db9ee4a84251e5`.
- Windows GitHub Actions artifact ID `11528593129`, outer-wrapper SHA256 `17e9c36b2f6db95f99ba5fb9fa3a0e4234dd5c188191c12f625cb1cd105a9431`; expires 22 Oct 2026 UTC.
- Evidence: `docs/planning/audits/STEP12_PORTABLE_RELEASE_INTEGRITY_EVIDENCE_2026-10-08.md`.
- Latest handoff: `docs/handoff/current/HANDOFF_STEP12_PORTABLE_QA_TO_MANUAL_GATE_2026-10-08.md`. R00–R04 offline audit unchanged, no live provider actions.

## 8 October 2026 — SOL independent Hasil export concurrency hardening PASS
- Fixed `ResultManifestWriter.write` concurrent static-temp collision via a uniquely owned NamedTemporaryFile, flush/fsync, atomic same-directory replace and own-temp cleanup.
- Deterministic two-writer barrier regression and injected replace/partial-write failure tests PASS. Previous final manifest survives failed publication; no orphan temp.
- Schema v1.0 and UI unchanged. Concurrent successful exports still have last-writer-wins semantics; no optimistic stale-snapshot fencing claimed.
- PR #19 merged code/tested `42afad61a6bde7798623d807de2c74c51339fe82`; official main CI `37729402213` **SUCCESS**: 220 passed, Ruff/mypy/architecture PASS, UI 30/30 PASS, Chromium + Windows portable/smoke + ZIP verification PASS.
- Windows artifact ID `11529730338` sha256 `ccf0aa7d64ddb967d5732952970aa7785f140fa8f579f4906659869b4d9b7272`, expires 2026-10-22; internal portable ZIP sha256 `242beb868acf5d2e190ba0f746963d607b1493aea258b34213d84fa2714da97d`.
- Evidence `docs/planning/audits/STEP12_MANIFEST_ATOMIC_EXPORT_EVIDENCE_2026-10-08.md`; handoff `docs/handoff/current/HANDOFF_STEP12_MANIFEST_EXPORT_SAFE_2026-10-08.md`.
- User reported Google manual login possible; READY-after-app-restart proof not supplied. Flow live remains BLOCKED, no live actions tested.

## 8 October 2026 — SOL LocalResults late failure regression COMPLETE / PASS
- Fixed a missed R03 history-protection path: `LocalResultsService.record_download_failed` now uses existing atomic `save_failure_if_unconfirmed`, not unconditional `save`, and returns effective persisted state. Confirmed DOWNLOADED history, output path and editing handoff survive late FAILED reports.
- New real SQLite/Workspace/Qt-compatible integration regressions: normal failed outcome, delayed failure after successful download, and cross-service delayed failure. No port/schema/architecture/UI change.
- PR #20 merged code `8149309540233a3a9255b6a2610cfb2554937ed1`, official tested main CI `37730824287` **SUCCESS**: Ruff/mypy/architecture PASS, **223 tests**, **30/30 frozen UI**, staged Chromium + Windows portable build/smoke + verified ZIP PASS.
- Windows artifact ID `11529054245`, SHA256 (outer archive) `a3254d36eafc023647908f790ecc693fdb43e01793fd096aeea502cdb5ecf1c5`; inner ZIP SHA256 `07bd9418bd37eea491e58484650b5e674df18773b0e711343ad187c629bdfb5c`. Artifact expires 22 Oct 2026 UTC.
- Evidence: `docs/planning/audits/STEP12_LOCAL_DOWNLOAD_FAILURE_HISTORY_EVIDENCE_2026-10-08.md`; handoff: `docs/handoff/current/HANDOFF_STEP12_LOCAL_DOWNLOAD_HISTORY_SAFE_2026-10-08.md`.
- Manual Google login reported working but post-restart READY proof absent; all live Google Flow operations still blocked.

## 8 October 2026 — SOL SQLite Download History Read-Only QA COMPLETE / PASS
- Confirmed legacy-project bug: `SqliteDownloadResultRepository.get` / `list_for_episode` previously created missing download_results table on reads. Both now open `mode=ro` and inspect `sqlite_master`; no DDL, legacy DB mutation or accidental creation. Explicit write logic unchanged.
- Real SQLite regressions: missing DB, legacy no-table checksum/no-journal, existing download history checksum, corrupt DB byte preservation all PASS.
- PR #21 merged code `936279f71d1a2863a5b9a0f61923d9b226c1b0a2`; official merged-main CI `37732145080` SUCCESS: **227 pytest**, Ruff/mypy/architecture, frozen UI **30/30**, staged Chromium + Windows portable smoke and ZIP checksum/CRC/source verifier PASS.
- GitHub Windows artifact `11530112083` (outer sha256 `789bb3c1afd5106580180f9b288e4067665b203e5477519ff291f6a8c02e9056`), inner ZIP sha256 `480ef6a8c08036990cf458b8f0c0ec2971aa47a031b29ea12112a461c3f357b6`, expires 22 Oct 2026 UTC.
- Evidence `docs/planning/audits/STEP12_DOWNLOAD_HISTORY_READONLY_EVIDENCE_2026-10-08.md`; handoff `docs/handoff/current/HANDOFF_STEP12_DOWNLOAD_READONLY_2026-10-08.md`.
- User's Google login works per report; READY after full app restart unverified. No Google Flow live test authorized/performed.


## 8 October 2026 — Hasil error recovery audit
- Fixed Hasil navigation and export callbacks leaking expected errors into Qt, plus untyped Download timestamp/take decode failures.
- COMPLETE / PASS: baseline 227 tests; patched full suite 233 PASS locally and on Windows. Official PR CI `37733697262` all jobs SUCCESS: Ruff/mypy/architecture, 30/30 frozen UI, Chromium/portable smoke and ZIP integrity verification PASS.
- Prior export file preserved on publication failure; UI reports a safe Indonesian message and permits explicit retry. Read-only history semantics retained.
- Evidence/handoff: `docs/planning/audits/STEP12_RESULTS_ERROR_RECOVERY_2026-10-08.md`.
- PR #22 merged as `1c7ade1922e45b987a45f495fb0784588a3c1291`; merged source tree equals verified PR head `a0041755e3635795c489702a67353aa2df1a63ab`.
- STEP 12 and live Google restart/Generate/Download gates unchanged.


## 2026-10-08 — E12-00 document alternatives / PR #23
- [x] E12-00 text authority coverage checked: V1.0 30/30 page markers and 45 test IDs; V1.1 32/32 markers, 17 waves, 90 task IDs and 15 X tests; E12-00 T01–T05 present.
- [x] V1.1 and E12-00 TXT+MD and reconstructed DOCX uploaded to the **review branch only**, verified Git SHA/size; parent V1.0 archived in MD.
- [x] Differences recorded: 42 original V1.1 Word tables and 9 original E12-00 tables are flattened in text reconstructions; no byte-identity or visual parity claimed. See `docs/planning/audits/E12_00_TEXT_EQUIVALENCE_AND_G0_LIMITS_2026-10-08.md`.
- [ ] **G0 strict BLOCKED**: original DOCX preservation/equivalence approval not completed. Do not begin SOL coding/Generate or edit frozen UI.
- [ ] NEXT: E12-01 ASTRA ADR-020–023 planning review only; keep policy/credits/login/live gates blocked independently.


## 8 October 2026 — ASTRA E12-01 Decision & ADR Review (PLANNING ONLY)
- [x] T01 ADR-020 draft: global reservation, cross-project spend safety, outbox and transaction authority.
- [x] T02 ADR-021 draft: authorized profile, policy checks, observable credit freshness, budget limits.
- [x] T03 schema/migration candidate: existing schema v2 and result manifest v1 compatibility, create-only coordinator, no-loss rollback.
- [x] T04 ADR-022 draft: submit boundary, held UNKNOWN, remote ID, download/recovery contracts.
- [x] T05 ADR-023 draft: actor/thread ownership, scoped leases/fences, fake-first multi-profile scheduling.
- [ ] T06: validate proposed ADR-020–023 with ASTRA/owner, resolve open decisions and record signoff; **NOT IMPLEMENTED**.
- [ ] G0 strict DOCX authority/visual equivalence remains BLOCKED; G1 policy, G5 actual tariff/credit, G6 restart READY unverified.
- [ ] Do NOT start E12-02 UI prompts/coding from this task without explicit NEXT wave authorization and UI STOP checkpoint. No production file edits on this PR.

## 8 October 2026 — E12-02 UI prompt checkpoint
- [x] T01: Inventory 9 UIX extension groups and 22 image states, using existing 30 frozen UI references.
- [x] T02: Prepare prompt matrix and self-contained prompt variants; downloadable DOCX and ZIP available in conversation.
- [x] T03: Mandatory STOP after prompt preparation; no generated UI images yet.
- [ ] T04: Create/review/approve each image with user input; not started.
- [ ] T05: Consolidate all approved UI images into one final reference DOCX; not started.
- [ ] G4 UI freeze BLOCKED; G0 strict and provider gates remain blocked. No code or E12-03 work.


## E12-02 review of all 22 UI mockups — 2026-10-08 (on PR #25 only)
- [x] UIX-01-A through UIX-09-B: 22 draft mockups created; each V2 PNG 1920×1080; independent ZIP/manifest SHA-256 and review DOCX embedded-image validation **22/22 PASS**.
- [x] Image hash and 22-ID visual-approval checklist recorded in `docs/ui/review/E12_02_V2_22_IMAGE_MANIFEST_AND_OWNER_SIGNOFF_PENDING_2026-10-08.md` (GitHub text only).
- [ ] **Owner must explicitly approve all exact 22 V2 images** or request corrections by ID; technical integrity does not mean visual approval.
- [ ] Consolidate approved 22 PNG into one **FINAL** UI reference DOCX and obtain reference-DOCX signoff; current V2 DOCX is REVIEW ONLY and NOT in GitHub.
- [ ] Original PNG binaries and final DOCX must be put in repo and verified before any UI G4 PASS claim; PR #25 must stay draft/unmerged pending UI approval.
- [ ] **BLOCKED**: UI G4, strict G0, E12-01 ADR T06, provider G1/G5/G6. No code, E12-03, real Generate/Download or credits.
