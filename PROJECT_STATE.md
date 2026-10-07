# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Factory STEP completed: STEP 11 — Feature Implementation Waves
- STEP 11 status: PASS
- Last tested implementation SHA: 75a896ccf3754a225414c34de9f88d5d9a8b5581
- Final STEP 11 CI run: 37597279499 — SUCCESS
- Quality job: 112712882373 — SUCCESS
- UI regression job: 112713211791 — SUCCESS
- Windows package job: 112713484132 — SUCCESS
- UI regression artifact ID: 11471336385
- UI regression artifact digest: sha256:738549ef6b86e9c51530e604ac9758914eea823b2fdd2181df8cc831f3d35d02
- Windows portable artifact ID: 11471780918
- Windows portable artifact uploaded size: 395656819 bytes
- Windows portable artifact digest: sha256:b85a3541f03524d65c439912dd4c7afd98ab1727c7661b5cf5487e73895b481d
- Live Google login / Google Flow generation / live Flow download / Gemini provider: NOT TESTED

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
- NEXT: STEP 12 — Integrations & External Services

## STEP 11 delivered waves

### W11-01 — Scene Planning & Readiness
PASS.
- User-selected Flow duration 4/6/8/10 is persisted per Scene.
- Invalid selections shorter than authoritative Target are rejected.
- Normal planning actions never rewrite Target.
- Approved-image rescan uses the existing package/filesystem owner.
- Scene readiness is recomputed after duration/image changes.
- Frozen Workspace/Scene Inspector controls invoke real application commands.
- Selection survives save/reload.
- Local planning remains independent from live Google/provider behavior.

### W11-02 — Local Project Hub / Recent Project / Recovery
PASS.
- Local Project Hub reads persisted per-project SQLite state.
- Recent projects are returned newest first.
- Persisted workspaces can be reopened/recovered into the active application session.
- Frozen Beranda/Project Hub is reused rather than redesigned.
- Recovery proven here means local persisted-state reopen; ambiguous external-provider recovery remains STEP 12/13 work.

### W11-03 — Durable Serial Local Queue / Fake Provider
PASS.
- Durable GenerationJob and GenerationJobState introduced.
- Generation queue persists in per-project SQLite.
- R1 serial claim rule prevents a second claim while one job is RUNNING.
- Queue preparation is idempotent per Scene.
- Provider-neutral GenerationRequest/Result boundary exists.
- Deterministic fake provider evidence proves local queue transitions.
- No live Google Flow adapter is wired in STEP 11.

### W11-04 — Local Results / Handoff Manifest
PASS.
- Generate and Download states remain separate.
- Local Download outcomes persist separately from Generate jobs.
- Download success is rejected before Generate reaches GENERATED.
- Download success also requires a real local output file.
- Real Hasil screen reads local persisted facts.
- FLOW_OTOMATIS_RESULT.json is written atomically and contains no credential/cookie/token fields.
- Handoff-ready requires all Scene downloads to be locally recorded as DOWNLOADED.
- Frozen Hasil compositions are reused without silent redesign.

## Final STEP 11 automated evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 51 source files.
- architecture guard: PASS.
- pytest: 43 passed.
- Frozen UI regression: 30/30 PASS.
- Visual similarity range: 0.6344–0.9643 at threshold 0.55.
- Playwright Chromium staging/smoke: PASS.
- PyInstaller onedir build: PASS.
- Portable application smoke: PASS.
- STEP 11 Windows artifact: Flow-Otomatis-step11-feature-waves-win-x64.
- STEP 11 UI evidence artifact: Flow-Otomatis-step11-ui-regression-evidence.

## Architecture/product rules still frozen
- CPython 3.14.x x64 + PySide6 Qt Widgets.
- Playwright Chromium belongs to the dedicated Browser Worker / provider boundary.
- Modular monolith + ports/adapters.
- SQLite per-project persistence.
- Windows Credential Locker/keyring for secrets.
- PyInstaller onedir portable ZIP.
- Serial R1 generation queue.
- Omni Flash 1.1 • 720p • 16:9.
- Audio/SRT Target is authoritative.
- Flow duration values are 4/6/8/10.
- Generate and Download remain separate states.
- No CAPTCHA/MFA bypass.
- No credential export.
- No hidden account rotation or quota/rate-limit evasion.
- STEP 09 frozen UI cannot be silently redesigned.

## Known limitations after STEP 11
- Generation provider remains fake/local for STEP 11 evidence.
- Real Google account login/session lifecycle is NOT TESTED.
- Live Google Flow submit/generation is NOT TESTED.
- Live result detection/download is NOT TESTED.
- Gemini AI Agent/API behavior is NOT TESTED.
- External timeout/cancel/retry/auth/rate-limit mappings are not yet proven.
- Local Project Hub recovery does not yet resolve ambiguous external jobs.
- Existing PySide6 QTableWidgetItem.setTextAlignment(int) deprecation warnings remain non-blocking.
- PyInstaller emitted a non-blocking hidden-import warning for tzdata; packaged smoke still passed.

## STEP 12 contract
Software Factory defines STEP 12 as **Integrations & External Services**.
Every external integration must define and test:
- interface/contract;
- timeout and cancel behavior;
- safe retry/idempotency policy;
- permission/auth state;
- credential storage/redaction;
- malformed/partial response handling;
- network/offline behavior;
- stale-response prevention;
- diagnostics/error mapping;
- fixture/mock mode.

## Recommended STEP 12 order
1. **I12-01 — Authorized Google Session / Manual Login Lifecycle**
   - user-owned profiles only;
   - persistent authorized browser contexts;
   - manual login/MFA/CAPTCHA only;
   - session status/check/recovery;
   - no credential extraction or bypass.
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
Start STEP 12 only after the product owner says "lanjutkan".
Begin with I12-01 and keep live provider work incremental. Do not collapse all external integrations into one change.
