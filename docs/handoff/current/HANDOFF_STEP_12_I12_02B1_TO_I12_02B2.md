# HANDOFF — STEP 12 / I12-02B1 → I12-02B2

## Gate
I12-02B1 — Read-Only Google Flow Preflight: **PASS**

I12-01 remains **AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING**.

I12-02B2 — Live One-Scene Google Flow Submit Driver: **BLOCKED** until the real-account session gate passes.

## Tested baseline
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- Tested implementation SHA: `8ebd5a5e048c1a3c606c2ace4ddf17c8ef510780`
- CI: `37604743253` — SUCCESS
- Quality: `112737380299` — SUCCESS
- UI visual: `112737696541` — SUCCESS
- Windows package: `112737987743` — SUCCESS

## Delivered in I12-02B1
### Shared Chromium ownership
`workers/browser/browser_context_pool.py`
- PlaywrightPersistentContextPool
- one profile id → one persistent browser context
- preserves browser-data on context close
- central shutdown

`PlaywrightGoogleSessionDriver` now delegates context ownership to the pool.

This allows a future Flow adapter and the session lifecycle to share the same user-owned profile context instead of opening competing persistent contexts on the same browser-data directory.

### Read-only Flow preflight
`application/ports/google_flow_preflight.py`
- GoogleFlowAccessState
- GoogleFlowAccessProbe
- GoogleFlowPreflightPort

`application/services/google_flow_preflight.py`
- GoogleFlowPreflightService

`workers/browser/google_flow_preflight.py`
- GoogleFlowPreflightDriver
- PlaywrightGoogleFlowPreflightDriver
- GoogleFlowPreflightWorker

Official navigation target:
- `https://labs.google/fx/tools/flow`

State mapping:
- labs.google → REACHABLE
- accounts.google.com → AUTH_REQUIRED
- HTTP >= 400 → UNAVAILABLE
- navigation timeout → UNKNOWN
- browser error → ERROR

REACHABLE means only that the official Flow page was reachable. It does not mean generation works.

## Explicit non-actions
I12-02B1 does not:
- upload media;
- type prompts;
- choose generation settings;
- discover/lock mutating selectors;
- click Create/Generate;
- intentionally consume credits;
- inspect private cookies/tokens;
- export browser session data.

## Evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 60 source files.
- architecture guard: PASS.
- pytest: **59 passed**.
- visual regression: **30/30 PASS**.
- similarity: **0.6344–0.9643**.
- Chromium staging/smoke: PASS.
- PyInstaller onedir: PASS.
- portable smoke: PASS.

Artifacts:
- `Flow-Otomatis-step12-i12-02b1-readonly-preflight-ui-evidence`
  - ID: `11473953895`
  - digest: `sha256:37de328dbe47abd5ba8a9114c9a0999d3e1be8c46d46534cd9a729499f69465b`
- `Flow-Otomatis-step12-i12-02b1-readonly-preflight-win-x64`
  - ID: `11474421936`
  - size: `435464521` bytes
  - digest: `sha256:0cf17a7590251cfa775b502401eddaaf5b3a1bfef1f445229844387b13bced16`

## Gate before I12-02B2
Product owner must validate on Windows:
1. create/open a local Google profile;
2. manually login;
3. Cek Ulang Sesi reports Siap;
4. fully close app;
5. reopen;
6. same profile remains usable if Google retained the session.

Do not provide password, MFA code, cookies, tokens, or browser-data as evidence.

## Next exact action
After that validation succeeds and product owner says **“lanjutkan”**, implement I12-02B2 for exactly one Scene.

Required rules:
- current verified Flow UI only;
- Browser Worker only;
- one mutating submit attempt maximum;
- no automatic retry;
- ambiguous outcome → ATTENTION_REQUIRED;
- no result download in I12-02B2;
- no Gemini integration in I12-02B2.
