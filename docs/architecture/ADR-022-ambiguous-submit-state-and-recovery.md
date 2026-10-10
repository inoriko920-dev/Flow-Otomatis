# ADR-022 — Durable Submit Boundaries, Ambiguity and Recovery (E12-01)
Status: **OWNER-APPROVED ARCHITECTURE DESIGN — T06 D02/D04/D06 PASS; TESTS NOT RUN / NO CODE AUTHORIZED** • 8 Oct 2026 WIB • Baseline: `978dbb31ce2024da0c70280f260f421e2687382b`

> **2026-10-09 OWNER SIGNOFF — T06 architecture DESIGN ONLY.** The owner explicitly agreed to D01–D06 after being asked to approve their final design. Full scope and gate consequences: `docs/planning/decisions/E12_01_T06_OWNER_APPROVED_SIX_ARCHITECTURE_DECISIONS_2026-10-09.md`. D04 canonical submit boundary is SUBMIT_STARTED before mutation, SUBMIT_UNCERTAIN retains original-account hold, and only account-bound conclusive no-acceptance proof allows FAILED_SAFE. D02 immutable identity and D06 no-loss rollback remain binding; new fake failure/recovery tests have NOT run. This does **not** grant permission to code, merge PRs, migrate existing databases, operate Google Flow or spend credits. Any references below to "candidate"/"proposed" describe the historical draft that was accepted as an architecture design, not a claim of implemented behavior.

References: ADR-016 coherent request + lease, ADR-019 no-clobber download and existing `GenerationJobState` enum.

## Context / compatibility
Legacy `QUEUED/RUNNING/GENERATED/ATTENTION_REQUIRED/FAILED` in project SQLite remains unchanged; never silently remap legacy rows to live-safe statuses. Coordinator uses its own **orthogonal, versioned** orchestration state and projects semantic status to existing UI via a typed adapter.

## Candidate state transitions
`PLAN_DRAFT -> PLAN_FROZEN -> RESERVED -> CLAIMED -> PRE_SUBMIT -> SUBMIT_STARTED`.
From `SUBMIT_STARTED` only `ACCEPTED`, `SUBMIT_UNCERTAIN`, or `FAILED_SAFE` (**conclusive evidence proves that no chargeable provider submission was accepted**). Accepted -> `GENERATING -> GENERATED -> DOWNLOAD_QUEUED -> DOWNLOADING -> DOWNLOADED`.
`SUBMIT_UNCERTAIN -> RECONCILING -> (ACCEPTED | ATTENTION_REQUIRED)` by **read-only evidence**, never blind repeat.
`PLAN_FROZEN -> PLAN_STALE` on asset, input digest, price/eligibility or selected profile change. `RESERVED/PRE_SUBMIT -> RELEASED_SAFE` ONLY if provably before any provider mutation and no extant attempt.
Unrecognized state => BLOCKED and diagnostics. No implicit success based on UI progress only.

## Durable ordering and crash rules
- Persist one immutable request snapshot/fingerprint (including image digest), plan revision, account profile and approved max cost **before claim**. Revalidate immediately before submit.
- Record `SUBMIT_STARTED` in the coordinator and flush commit **before** mutating remote UI; this is a conservative ambiguity boundary. A crash immediately after commit but before click is ambiguous and **stays held**, requiring evidence-based reconciliation rather than unsafe auto-retry.
- Owner fence, attempt ID, authorized profile and expected stable remote result identity accompany every callback. Out-of-order callbacks fail closed.
- `ACCEPTED` requires a stable remote ID and correct profile. A loading indicator, timeout, absent ID or connection reset is not sufficient acceptance/safe failure evidence.
- `FAILED_SAFE` is the **only canonical safe-failure state name** (do not introduce a separate `SAFE_FAILURE` enum). It requires durable, account-bound evidence proving that the provider did not accept a chargeable mutation. Timeout, absence of a remote ID, restart, or browser disconnect alone is **not** proof of safe failure. `SUBMIT_UNCERTAIN` holds the reservation and blocks automatic resubmit, account transfer and quota-driven rotation.
- Projections to per-project SQLite are idempotent; crash between global COMMIT and project update triggers outbox replay, never new Generate.
- Download is separately queued; use existing `GeneratedMediaDownloadProviderPort`, ADR-019 unique .part and NTFS no-clobber final publication, confirm nonempty file; DB write fail after publish requires file checksum/manual reconciliation, never deletion or overwrite.

## Recovery policy matrix
1. Before coordinator reservation COMMIT: no job, safe plan retry.
2. After reservation COMMIT before any PRE_SUBMIT evidence: recover stale owner with fence and new validation.
3. PRE_SUBMIT with conclusive no-click evidence: may release; otherwise hold.
4. SUBMIT_STARTED remote outcome unknown: ATTENTION + read-only reconciliation; never auto retry.
5. ACCEPTED with remote ID: poll read-only until ready; do not generate again.
6. DOWNLOADING and final path already present: no-clobber, inspect file and DB evidence, manual reconciliation if inconsistent.
7. Account logout/model unsupported/credits expired: pause only affected profile/new claims; never silently transfer an uncertain attempt.
8. Shutdown or second running app: prevent new writer/claim, preserve leases and evidence; recover after **fresh verification** in the new application process. A stored `READY_VERIFIED` proof from an earlier process is historical audit data, not current session permission.

Acceptance: X04-X10, X13 and original T03/T08/T12/T20/T22/T33 (as applicable). Tests inject crashes at every commit/action boundary using fake provider; no paid provider testing before G1/G6/G7/G8.
