# HANDOFF — STEP 12 / I12-02B2-PRECHECK → I12-02B2-LIVE

## Gate
I12-02B2-PRECHECK — Pre-Submit Request Guard: **PASS**

I12-01 remains **AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING**.

I12-02B2-LIVE — Live One-Scene Google Flow Submit Driver: **BLOCKED** until the real-account session gate passes.

## Tested baseline
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- Tested implementation SHA: `827c8f756b44cef94d5edeb5588fc1979cad8b07`
- CI: `37605969763` — SUCCESS
- Quality: `112741397608` — SUCCESS
- UI visual: `112741803066` — SUCCESS
- Windows package: `112742072939` — SUCCESS

## Delivered in PRECHECK
`application/ports/generation_provider.py`
- added `GenerationRequestValidationError`.

`workers/browser/google_flow_request_plan.py`
- `PreparedGoogleFlowRequest`
- `prepare_google_flow_request(...)`

Validation contract before any driver call:
- episode_id required;
- scene_id required;
- image_file required;
- motion_prompt required;
- target_duration_s > 0;
- flow_duration_s ∈ {4, 6, 8, 10};
- target_duration_s <= flow_duration_s;
- model == Omni Flash 1.1;
- resolution == 720p;
- aspect_ratio == 16:9.

`GoogleFlowGenerationProvider.generate(...)` now validates the request before invoking `submit_one(...)`.

Integration tests prove invalid requests leave driver call count at zero.

## Why this is required
Live Flow generation is a mutating external action and can consume credits. A request with the wrong duration/model/resolution/aspect ratio must therefore fail locally instead of reaching the browser.

This guard complements the existing I12-02A ambiguous-submit protection:
- bad request → fail before mutation;
- ambiguous post-mutation outcome → ATTENTION_REQUIRED;
- no automatic retry.

## Automated evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 61 source files.
- architecture guard: PASS.
- pytest: **75 passed**.
- visual regression: **30/30 PASS**.
- similarity: **0.6344–0.9643**.
- Chromium staging/smoke: PASS.
- PyInstaller onedir: PASS.
- portable smoke: PASS.

Artifacts:
- `Flow-Otomatis-step12-i12-02b2-precheck-ui-evidence`
  - ID: `11474916989`
  - digest: `sha256:4b53a1d7f922664dab277ecfa005ebbc9bddf72373772cd59cec6d2641498e5f`
- `Flow-Otomatis-step12-i12-02b2-precheck-win-x64`
  - ID: `11474334971`
  - size: `435465430` bytes
  - digest: `sha256:f719cbd338b95febec821788dbdef8f1693947a319d2ad8714c4fd81aa7d2d8a`

## Not implemented / not proven
- no live Flow project open/create automation;
- no live upload;
- no live prompt entry;
- no live settings selector;
- no live Generate click;
- no remote result id discovery;
- no live result/download.

Do not claim generation works live.

## Gate before I12-02B2-LIVE
Product owner must validate on Windows:
1. create/open a local Google profile;
2. manually login;
3. Cek Ulang Sesi reports Siap;
4. fully close app;
5. reopen;
6. same profile remains usable and Cek Ulang Sesi reports Siap where Google retained the session.

Do not provide password, MFA code, cookies, tokens, or browser-data as evidence.

## Next exact action
After that validation succeeds and product owner explicitly says **“lanjutkan”**, implement I12-02B2-LIVE for exactly one Scene.

Rules:
- inspect current authorized Flow UI before locking selectors;
- Browser Worker only;
- one mutating submit attempt maximum;
- never automatically retry;
- ambiguous outcome → ATTENTION_REQUIRED;
- do not combine result download or Gemini with this slice.
