# A03 Request Revision / Lease / Recovery Evidence — 7 October 2026

## Gate
A03: **PASS**.

## Scope
Closed F03 and F06 only. A04/F05 was not implemented.

## Implementation
- baseline before A03 docs: `c0417c8d0512cda82f404921fc95da163f39f277`
- PR #3 final head: `4733d55ad6c36fe5611f36278e1e60f1898fa8da`
- merge: `3ee8d8118c1a137ac5c24d6ed7896b15bb3ccafb`

Changed implementation/test files:
- `application/ports/generation_jobs.py`
- `application/services/local_generation_queue.py`
- `domain/job/__init__.py`
- `domain/job/model.py`
- `infrastructure/persistence/sqlite_generation_job_repository.py`
- queue/results/import/result-view regression tests.

## F03 evidence
Each prepared job stores the complete provider-relevant Scene snapshot and a deterministic SHA-256 fingerprint. Before dispatch, current Scene readiness, image availability, selected duration, request values, and fingerprint must still match. A mismatch becomes `ATTENTION_REQUIRED / REQUEST_STALE` with zero provider call. Explicit re-prepare creates a new coherent revision.

## F06 evidence
RUNNING work stores:
- owner identity;
- lease expiry;
- submit-started boundary.

An active lease cannot be stolen. Expired work before submit is classified separately from expired work after the submit boundary. Both require attention; possible-submit work is never automatically resubmitted.

## Migration evidence
The generation-job schema migration is versioned and transactional. Legacy unverifiable queued/running rows are parked safely. Regression tests prove rollback on migration failure and preservation of confirmed GENERATED state, remote result identity, timestamps, and existing downloaded-result linkage.

## Regression coverage
- Scene edit after enqueue;
- image missing after enqueue;
- explicit re-prepare with new coherent revision;
- competing claimant protection;
- active-owner protection;
- expired lease before submit;
- expired lease after submit boundary;
- ambiguous submit remains blocked;
- legacy queue migration;
- migration rollback;
- confirmed result/download preservation.

## Official main CI
Run `37651619177`: SUCCESS.

Quality `112896105913`:
- Ruff format/lint PASS;
- mypy PASS — 63 source files;
- architecture PASS;
- pytest PASS — 106 passed, 1904 warnings.

UI `112896465371`:
- 30/30 PASS;
- similarity 0.6344–0.9643;
- artifact `11496781147`;
- SHA-256 `6e4ea19f855ebd96338421793f5ab90c9f3ba3219f09a7f272a78444984d467c`.

Windows `112896815896`:
- Chromium smoke PASS;
- portable build/smoke PASS;
- artifact `11497130854`;
- size 435495092 bytes;
- SHA-256 `5de387b7279a369ee4d4e51f041ad396be1bf77357f58696c1796675cdb58d5f`.

F05 remains open for A04. Existing live-operation safety gates remain unchanged.
