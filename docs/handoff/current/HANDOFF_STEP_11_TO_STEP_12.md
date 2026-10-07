# HANDOFF STEP 11 → STEP 12

## Gate
STEP 11 — Feature Implementation Waves: **PASS**

## Project / tested baseline
- Project: Flow-Otomatis
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- Last tested implementation SHA: `75a896ccf3754a225414c34de9f88d5d9a8b5581`
- Final STEP 11 CI run: `37597279499` — SUCCESS
- Quality job: `112712882373` — SUCCESS
- UI visual job: `112713211791` — SUCCESS
- Windows package job: `112713484132` — SUCCESS

## STEP 11 delivered waves

### W11-01 — Scene Planning & Readiness
- Flow-duration selection 4/6/8/10 is a real persisted command.
- Selection shorter than Target is rejected.
- Target remains immutable.
- Approved-image rescan recomputes readiness.
- Frozen Workspace/Scene Inspector controls operate on real state.

### W11-02 — Local Project Hub / Recovery
- Project Hub reads persisted local project state.
- Recent projects can be reopened after restart.
- This proves local recovery only, not ambiguous external-job recovery.

### W11-03 — Durable Serial R1 Queue
- Generation jobs are durable in per-project SQLite.
- Only one job can be RUNNING/claimed at a time.
- Queue preparation is idempotent.
- Provider-neutral GenerationRequest/GenerationProviderPort is the canonical integration seam.
- STEP 11 uses a fake provider only.

### W11-04 — Local Results / Handoff
- Generate and Download remain separate state machines.
- Download outcomes persist separately.
- Local output must exist before Download can be marked successful.
- Real Hasil UI renders local persisted facts.
- `FLOW_OTOMATIS_RESULT.json` is atomically exported without credential/session data.

## Canonical owners to preserve
- Scene timing/readiness: `domain/scene/model.py`
- Workspace: `domain/project/workspace.py`
- Generation jobs: `domain/job/`
- Results: `domain/result/`
- Package import: `application/services/episode_import.py`
- Scene planning: `application/services/scene_planning.py`
- Local queue: `application/services/local_generation_queue.py`
- Local results: `application/services/local_results.py`
- Provider boundary: `application/ports/generation_provider.py`
- Browser worker/provider integration must not be placed directly in presentation.
- Per-project SQLite adapters remain under `infrastructure/persistence/`.
- Frozen presentation remains source-of-truth unless a formal UI Change Request is approved.

## Final evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 51 source files.
- architecture guard: PASS.
- pytest: **43 passed**.
- Frozen visual regression: **30/30 PASS**.
- Similarity: **0.6344–0.9643**, threshold 0.55.
- Chromium staging/smoke: PASS.
- PyInstaller onedir build: PASS.
- Portable application smoke: PASS.

Artifacts:
- UI regression: `Flow-Otomatis-step11-ui-regression-evidence`
  - ID: `11471336385`
  - digest: `738549ef6b86e9c51530e604ac9758914eea823b2fdd2181df8cc831f3d35d02`
- Windows package: `Flow-Otomatis-step11-feature-waves-win-x64`
  - ID: `11471780918`
  - size: `395656819` bytes
  - digest: `b85a3541f03524d65c439912dd4c7afd98ab1727c7661b5cf5487e73895b481d`

## Important NOT TESTED
- real Google account login/session persistence;
- live Google Flow submit/generation;
- live result detection and Flow download;
- live timeout/cancel/auth/rate-limit behavior;
- Gemini API / AI Agent external behavior;
- ambiguous external-job recovery after crash/network interruption.

Do not claim any of the above is ready from STEP 11 evidence.

## STEP 12 purpose
Software Factory STEP 12 = **Integrations & External Services**.

Every external adapter must define:
- input/output contract;
- timeout;
- cancel behavior;
- retry/idempotency;
- auth/session state;
- rate-limit/error mapping where applicable;
- malformed/partial response handling;
- offline/network-loss behavior;
- stale-response prevention;
- credential storage/redaction;
- mock/fixture mode;
- diagnostics.

## READY first integration
### I12-01 — Authorized Google Session / Manual Login Lifecycle
Goal: establish a safe user-owned browser session lifecycle before attempting live Flow mutation.

Required behavior:
1. create/open a named authorized profile context;
2. launch/focus official Google login when authentication is required;
3. user manually completes password/MFA/CAPTCHA;
4. detect Ready vs Needs Login without extracting credentials;
5. persist only the authorized browser context/session data in the user-scoped Session root;
6. expose deterministic status/check/recovery through the existing Profil Google / Bantuan Login UI;
7. redact session/credential data from logs, project DB, exports, and handoff manifests;
8. define timeout/cancel and shutdown behavior;
9. prove behavior with fixture/local controlled tests before any production Google mutation.

Hard prohibitions:
- no password/API token/cookie export;
- no CAPTCHA or MFA bypass;
- no automatic account rotation to evade quotas/free limits;
- no hidden credential reuse across unrelated profiles.

## Planned later STEP 12 integrations
- I12-02 — Google Flow Generation Adapter: one Scene first through Browser Worker, with ambiguous-submit protection.
- I12-03 — Live Result Detection & Download: verify local file before Download success.
- I12-04 — Gemini AI Agent / Key Integration: keyring-backed secrets, masked UI, bounded permissions.

## Exact next action
Wait for product-owner command **“lanjutkan”**.
Then start STEP 12 with I12-01 only. Do not collapse login, generation, download, and Gemini into one large integration change.
