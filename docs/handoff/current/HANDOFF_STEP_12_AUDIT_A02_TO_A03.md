# HANDOFF — STEP 12 AUDIT A02 → A03

## Gate
A02 — Corrupt-data isolation for F04: **PASS**.

This is the STEP 12 audit-remediation handoff. It does not authorize live Google Flow mutation.

## Verified baseline
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- A02 implementation merge: `9525a9d8ed370ab8b3f3ed916735e03ef04ecfce`
- Main CI: `37647427626` — SUCCESS
- Quality: `112881739521` — SUCCESS
- UI visual: `112882633481` — SUCCESS
- Windows package: `112883036794` — SUCCESS
- pytest: 99 passed
- mypy: 63 source files
- UI: 30/30 PASS
- Playwright Chromium smoke: PASS
- portable smoke: PASS

Evidence:
- `docs/planning/audits/A02_CORRUPT_DATA_ISOLATION_EVIDENCE_2026-10-07.md`

## Findings status
Closed:
- F01
- F02
- F04

Still open:
- F03 — queued request can mix stale duration/job state with newer Scene state.
- F05 — session checking can block the Qt event loop.
- F06 — orphan RUNNING jobs have no safe recovery classification.

## Next package — A03 only
A03 closes F03 and F06 and must follow ADR-016.

Owners:
- `LocalGenerationQueueService`;
- `GenerationJobRepositoryPort`;
- `SqliteGenerationJobRepository`;
- generation-job domain model;
- project reopen/recovery path.

Required design:
- persist a coherent generation request revision/fingerprint with the queued request;
- before provider dispatch, validate that the queued revision still matches current required Scene input/state;
- changed/unverifiable request state must block provider dispatch until explicitly prepared again;
- do not combine stale job duration with current prompt/image state;
- add durable owner identity and lease/liveness metadata for RUNNING work;
- only proven-orphan work may transition to an attention/recovery state;
- a second active instance must not steal work from a live owner;
- ambiguous submit must never be silently retried or auto-resubmitted;
- preserve remote result identifiers, download/result linkage, and historical timestamps.

Migration requirements:
- versioned and transactional;
- preserve existing job/result data;
- create/retain recovery evidence as required by the audit;
- failed migration must roll back cleanly;
- old jobs without a verifiable revision must not be submitted automatically;
- do not delete jobs merely to make new inserts succeed.

Primary tests:
- `tests/integration/test_local_generation_queue_wave.py`;
- `tests/integration/test_local_results_wave.py`;
- `tests/integration/test_project_library_wave.py`.

Acceptance scenarios:
- edit after enqueue;
- image becomes missing after enqueue;
- valid explicit re-prepare sends the new coherent revision;
- two claimants still yield at most one provider submit;
- second instance while owner is active does not take the job;
- crash before submit and crash/ambiguity after submit are distinguished safely;
- reopen classifies a true orphan to attention with zero automatic submit;
- GENERATED and downloaded results remain intact;
- migration rollback is clean.

Provider must remain fake/synthetic for this package. A03 does not enable the live Google Flow provider.

## Safety boundary
- no CAPTCHA/MFA bypass;
- no password/cookie/token/browser-profile export;
- no automatic account rotation;
- no guessed live selectors;
- no silent retry after ambiguous mutation;
- frozen UI remains authoritative;
- Flow durations remain 4/6/8/10;
- Audio/SRT Target remains authoritative;
- Generate and Download remain separate;
- I12-02B2-LIVE remains BLOCKED.

## Instruction to next SOL
After the product owner says `lanjutkan`, verify `main` still descends from the A02 baseline, read ADR-016 and current queue/result code, implement only A03, run targeted plus full Windows CI, update evidence/state/handoff, then stop before A04.
