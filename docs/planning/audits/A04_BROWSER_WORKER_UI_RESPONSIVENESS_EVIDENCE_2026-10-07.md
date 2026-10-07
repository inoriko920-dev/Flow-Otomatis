# A04 Browser Worker / UI Responsiveness Evidence — 7 October 2026

## Gate
A04: **PASS**.

## Scope
Closed F05 only. This package did not implement A05 and did not enable live Google Flow generation.

## Implementation identity
- A03 documentation baseline: `57821adf4dd8cb8f4eac8b927409b56f899f6b7e`
- work branch: `sol/a04-browser-worker-ui-responsiveness`
- PR #4 final head: `cdbbc8cf21ed9480b6c8d977a9597df0b3bbf066`
- main merge SHA: `837106d5e83839150706dfdf3857734308258184`

## F05 closure
The production composition now constructs one `ThreadedGoogleSessionCommands` owner with a single worker thread. Browser-touching operations for open-login, session checks, close/delete, and shutdown are submitted to that owner.

Qt:
- starts browser operations asynchronously;
- observes only `Future` completion;
- marshals sanitized results back using Qt Signals;
- never receives Playwright Page, Browser, or BrowserContext objects.

Ownership/concurrency:
- all queued browser session commands execute on the same worker thread;
- duplicate same-profile commands while a prior command is active are rejected with a safe application error;
- no second Browser Worker owner is created for the duplicate.

Timeout/cleanup:
- Chrome debug startup retains a bounded startup timeout;
- CDP connect has an explicit bounded timeout;
- navigation/probe retains the explicit driver timeout;
- MainWindow shutdown waits at most 1.5 seconds for Browser Worker cleanup;
- a bounded UI wait does not falsely claim to cancel a synchronous browser call already in progress; worker-owned cleanup completes on its owner.

Authentication compatibility:
- human sign-in still uses installed normal Google Chrome;
- there is no Playwright/CDP attachment during password, MFA, or CAPTCHA entry;
- automation attaches only after manual sign-in is finished and the login Chrome window is closed.

## Regression proof
New/updated tests prove:
- a deliberately slow session probe leaves a Qt timer/heartbeat advancing;
- same-profile duplicate checks do not start competing browser operations;
- browser session actions and shutdown execute on one worker thread, not on the caller/Qt thread;
- bounded shutdown returns without waiting indefinitely for a slow probe;
- returned profile results contain no browser runtime objects or session secrets;
- existing restart-proof and normal-Chrome lifecycle regressions remain green.

The audit's A04 fake-driver evidence does not prove a real Google account login. That validation remains a separate existing product gate.

## Official main CI
Run `37654708047`: SUCCESS.

Quality `112906749552`:
- Ruff format PASS — 133 files already formatted;
- Ruff lint PASS;
- mypy PASS — no issues in 64 source files;
- architecture guard PASS;
- pytest PASS — 110 passed, 1904 warnings.

UI visual `112907117114`:
- 30/30 fixtures PASS;
- similarity 0.6344–0.9643;
- artifact ID `11497423543`;
- size 3316911 bytes;
- SHA-256 `8e23610a8d36008c8d25aadd54b8baccf747dc3edfed7ac64e0997bc69084a35`.

Windows package `112907455169`:
- staged Playwright Chromium smoke PASS;
- portable build PASS;
- portable application smoke PASS;
- artifact ID `11497868670`;
- size 435501661 bytes;
- SHA-256 `0bea14b02d2a4faf85fb02b0dfe0d7d560d220c0aa0a3885e554c8ee31783267`.

## Finding status
F01 CLOSED.
F02 CLOSED.
F03 CLOSED.
F04 CLOSED.
F05 CLOSED.
F06 CLOSED.

## Boundary
A04 PASS means F05 is locally remediated on the official runtime. It does not mean a real Google session has passed restart validation, and it does not authorize I12-02B2-LIVE.
