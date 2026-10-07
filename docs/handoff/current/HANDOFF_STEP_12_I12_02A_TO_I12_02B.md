# HANDOFF — STEP 12 / I12-02A → I12-02B

## Gate
I12-02A — Deterministic Submit Contract & Ambiguous-Submit Guard: **PASS**

I12-01 remains **AUTOMATED PASS / LIVE MANUAL VALIDATION PENDING**.

I12-02B — Live Google Flow Playwright Driver: **BLOCKED** until I12-01 live validation succeeds.

## Tested baseline
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- Tested implementation SHA: `90fafb83821ff7ec82c3253d046293b780220edb`
- CI run: `37603714336` — SUCCESS
- Quality: `112734004875` — SUCCESS
- UI visual: `112734322641` — SUCCESS
- Windows package: `112734665287` — SUCCESS

## Why I12-02 was split
A live browser submit is mutating. If the browser times out after clicking Generate, automatic retry can create duplicate generations. I12-02A therefore establishes deterministic provider semantics before any real Flow selector is introduced.

## Canonical contract
`application/ports/generation_provider.py`
- GenerationProviderError
- GenerationSubmissionAmbiguousError
- GenerationAuthenticationRequiredError
- GenerationCancelledError
- GenerationRequest
- GenerationProviderResult
- GenerationProviderPort

`workers/browser/google_flow_generation.py`
- GoogleFlowSubmitState
- GoogleFlowSubmitEvidence
- GoogleFlowGenerationDriver
- GoogleFlowGenerationProvider

Evidence states:
- ACCEPTED
- SAFE_FAILURE
- AUTH_REQUIRED
- CANCELLED
- AMBIGUOUS

The provider makes exactly one `submit_one` driver call. There is no automatic retry loop.

## Durable queue rule
GenerationJobState now includes `ATTENTION_REQUIRED`.

The SQLite queue refuses to claim another QUEUED job while the episode contains:
- RUNNING; or
- ATTENTION_REQUIRED.

Mappings:
- ACCEPTED + stable remote_result_id → GENERATED
- ACCEPTED without stable remote id → ATTENTION_REQUIRED
- AMBIGUOUS → ATTENTION_REQUIRED
- AUTH_REQUIRED → ATTENTION_REQUIRED
- CANCELLED → FAILED with cancelled diagnostic
- SAFE_FAILURE → FAILED

This prevents an ambiguous Scene from being silently resubmitted and prevents Scene 2 from advancing while Scene 1 is unresolved.

## Automated evidence
- Ruff format: PASS.
- Ruff lint: PASS.
- mypy strict: PASS — 56 source files.
- architecture guard: PASS.
- pytest: **53 passed**.
- Frozen visual regression: **30/30 PASS**.
- Similarity: **0.6344–0.9643**, threshold 0.55.
- Chromium staging/smoke: PASS.
- PyInstaller onedir: PASS.
- Portable smoke: PASS.

Artifacts:
- `Flow-Otomatis-step12-i12-02a-contract-ui-regression-evidence`
  - ID: `11473099652`
  - digest: `sha256:34de8d0b0ddd910c40017b46c7e66a4fd37a3ac9e6107d720891296eb5253726`
- `Flow-Otomatis-step12-i12-02a-contract-win-x64`
  - ID: `11473888042`
  - size: `435454484` bytes
  - digest: `sha256:0d5eabc603acba99c0e7d5c09e3adcec51135e7a0bf8c37bdde97ad4ac332c99`

## Not implemented / not proven
- no live Google Flow selector;
- no live image upload;
- no live prompt typing;
- no live model/duration/resolution selection;
- no click on real Generate/Create;
- no live remote result id;
- no live provider timeout/cancel classification;
- no live result detection/download.

Do not claim Google Flow generation is working yet.

## Required gate before I12-02B
Validate I12-01 on the product owner's Windows machine:
1. create/open profile;
2. manually login to Google;
3. app reports Siap;
4. close app;
5. reopen app;
6. same profile/session remains usable if Google retained the session.

Do not share any password, MFA code, cookie, token, or browser-profile/session files.

## Next exact action
After successful live I12-01 validation and explicit **“lanjutkan”**, implement I12-02B for **one Scene only**.

Rules for I12-02B:
- Browser Worker owns Playwright.
- Reuse authorized user-owned profile.
- Verify current Flow UI before locking selectors.
- One mutating submit attempt maximum.
- Never retry after ambiguous outcome.
- Do not mix download/result detection or Gemini into I12-02B.
