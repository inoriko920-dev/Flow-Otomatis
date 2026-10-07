# A05 Combined Verification Run — 8 October 2026

Status: **PASS**

## Fresh tested SHA
- `7c1545c775fede2442a89d54d828e32813b9c8a5`
- Base before A05 marker: `de202a7fe15ec2a94a6c7aa6862742cdd82c18ff`
- A05 marker diff: documentation only; production source/tests/runtime unchanged before the fresh run.

## Acceptance matrix T01–T12
- T01 PASS — missing prompt TXT in ZIP/folder returns typed validation failure before persistence.
- T02 PASS — valid UTF-8, empty prompt, inline happy path, and ZIP traversal behavior remain consistent.
- T03 PASS — duplicate import is rejected atomically; prior workspace/jobs/downloads stay intact.
- T04 PASS — Scene edit after enqueue prevents stale/mixed provider dispatch until explicit re-prepare.
- T05 PASS — image loss after enqueue causes zero stale provider submit.
- T06 PASS — healthy project remains usable beside corrupt/unreadable project data; corrupt source remains unmodified.
- T07 PASS — slow session probe preserves Qt heartbeat and same-profile duplicate command does not start competing browser ownership.
- T08 PASS — Browser Worker shutdown wait is bounded while an operation is active; cleanup remains worker-owned.
- T09 PASS — expired/orphan RUNNING work transitions to ATTENTION_REQUIRED with no automatic provider submit.
- T10 PASS — a second owner cannot steal a live RUNNING lease.
- T11 PASS — generation-job migration preserves confirmed generated/download history and forced migration failure rolls back atomically.
- T12 PASS — fresh official runtime, complete regression suite, frozen UI visual regression, Windows portable build, Chromium smoke, and portable smoke all passed.

## Fresh official CI
Run `37656131625`: **SUCCESS**.

### Quality — `112911424702`
- Windows official runner
- CPython 3.14.7 x64
- uv 0.12.23
- `uv sync --frozen --all-groups`: PASS
- Ruff format: PASS — 136 files already formatted
- Ruff lint: PASS
- mypy: PASS — no issues in 64 source files
- architecture guard: PASS
- pytest: PASS — 110 passed, 1904 warnings

### Frozen UI visual — `112912268379`
- 30/30 fixtures PASS
- similarity range: 0.6344–0.9643
- artifact ID: `11499155505`
- artifact size: 3316911 bytes
- SHA-256: `8997ba4dfe5894a662f6e86719a4cad8c1dc25227ae709f1e138f9476b841749`

### Windows portable — `112912812398`
- staged Playwright Chromium smoke: PASS
- portable build: PASS
- portable application smoke: PASS
- artifact ID: `11500180694`
- artifact size: 435501172 bytes
- SHA-256: `9378857debe5a7812db9702d9e1ea9f54211cd8f029ceda0a6f96732519f57ca`

## Audit finding closure
- F01 CLOSED
- F02 CLOSED
- F03 CLOSED
- F04 CLOSED
- F05 CLOSED
- F06 CLOSED

## Final interpretation
A05 PASS means the **local STEP 12 audit-remediation track A00–A05 is complete and freshly verified**.

It does **not** mean the application is fully ready for live Google Flow:
- real Google-account login/restart persistence still requires manual validation on the user's Windows machine;
- I12-02B2-LIVE remains BLOCKED until that independent gate passes;
- no live Generate mutation was performed in A05;
- live result detection/download and Gemini integration remain outside this audit closure.
