# ADR-020 — Global Credit and Attempt Authority (E12-01)
Status: **OWNER-APPROVED ARCHITECTURE DESIGN — T06 D01/D02/D06 PASS; NOT IMPLEMENTED / NOT CODE-AUTHORIZED** • 8 Oct 2026 WIB • Baseline: `978dbb31ce2024da0c70280f260f421e2687382b`

> **2026-10-09 OWNER SIGNOFF — T06 architecture DESIGN ONLY.** The owner explicitly agreed to D01–D06 after being asked to approve their final design. Full scope and gate consequences: `docs/planning/decisions/E12_01_T06_OWNER_APPROVED_SIX_ARCHITECTURE_DECISIONS_2026-10-09.md`. D01 global single-device SQLite attempt/credit ledger and outbox; D02 immutable scoped identity/reservation/lease fencing; D06 additive feature-flagged migration and backup/rollback design. Existing project DB schema-v2 is not replaced, and fake race/crash acceptance has NOT been executed. This does **not** grant permission to code, merge PRs, migrate existing databases, operate Google Flow or spend credits. Any references below to "candidate"/"proposed" describe the historical draft that was accepted as an architecture design, not a claim of implemented behavior.

Scope: new optional coordinator model for future E12 waves, NOT production code.
Related: ADR-004, ADR-016, ADR-018/019, Master Plan V1.1, E12-01 DOCX.

## Problem and options
Existing `SqliteGenerationJobRepository` persists jobs in each project DB (schema v2). `claim_next()` enforces one serial job per episode, not global account reservations. An account may be selected by two projects; independent balances in each project can double-allocate the same credit.
- A: per-project reservations — REJECT for P0 double-allocation risk.
- B: multi-file ATTACH transaction — DEFER because atomic crash behavior/rollback with multi-file WAL is too fragile for the current product.
- C: **one local global coordinator SQLite DB**, and idempotent event projections into existing per-project stores — SELECTED AS PROPOSAL.

## Authority and location
- Candidate `PathService.settings_root / "coordination" / "coordinator.sqlite"`, one writable coordinator per Windows user; exact name pending E12-03. Never commit DBs, cache, session, or secret data.
- Coordinator exclusively owns `account_profiles` (references/consent only), `credit_snapshots`, `tariff_versions`, `plan_revisions`, `generation_attempts`, `credit_reservations`, `credit_events`, `worker_leases` and `outbox_events`.
- Existing project SQLite remains authority for imported scene/target/media, project identity and historical local generation/download. Global DB *does not rewrite* schema v2 or result manifest v1.0.
- Projection from coordinator to project uses at-least-once outbox with UNIQUE event_id receipt and replay; **eventual consistency is explicit**, never a two-DB ACID claim.
- A project ID is durable/opaque; avoid assuming episode_id alone is unique across all imported workspaces. Define scoped stable project key prior to migration.

## P0 invariants
1. Available credit for profile = `max(observed_balance - active_reservations - approved_safety_hold, 0)`; observed balance must be fresh, provider-sourced, eligibility verified. Manual values are **simulation only**. Never infer "50 credits/day".
2. `BEGIN IMMEDIATE` with a short busy timeout encloses **approval/fingerprint/tariff/snapshot/identity check, unique active attempt insert, credit reservation insert, event and outbox insert**. Any failure ROLLBACK; never call provider while holding a SQL transaction.
3. Unique active attempt for a `(project_id, scene_id, approved_plan_revision)` and UNIQUE reservation per attempt; account scope must not change after PRE_SUBMIT.
4. Integer nonnegative credit cost per output, multi-output multiplier and immutable tariff provenance. Distinguish **reserved/held** from **observed provider spend**. Unknown/ambiguous does not auto-release its hold.
5. Ledger append-only immutable evidence and UNIQUE idempotency_key for each state transition. No shadow mutable balance as source of truth.
6. Lease fencing epoch/token monotonically increases. Stale actor must fail writes and browser mutation gates; time expiry alone does not prove a remote submit did not occur.
7. One active local app writer/owner per coordinator via strong process lock and SQL lease; another app instance must be read-only or refuse dispatch. This is single-device scope only; shared/network filesystems are out of scope until separately reviewed.
8. Outbox events can be replayed after crash, but never authorize duplicate remote Generate.
9. If price/observed balance/account capability changes, **pause NEW claims**, invalidate unsubmitted plan and request reapproval; keep accepted/uncertain attempts for reconciliation.

## Candidate transactional interfaces — NOT IMPLEMENTED
`quote(plan, tariff_version, snapshot_id)`; `approve(plan_digest, cap, profile_opt_in)`; `reserve_and_claim(project_key, scene_revision, profile_id, fence)`; `mark_submit_started(attempt_id, fence)`; `record_remote_outcome(attempt_id, remote_id_or_ambiguity, evidence)`; `reconcile_snapshot(profile_id, proof)`; `emit_projection(event_id)`.
Ownership: pure `domain` invariants; `application/ports` commands; `infrastructure/persistence` SQLite; `bootstrap` composition ONLY.

## Migration, rollback, evidence
M0 inspect/backup old project DB without mutation; M1 create-only global schema in a transaction; M2 compatibility adapters preserve old read paths; M3 opt-in safe QUEUED migration only after exact request fingerprint check; M4 crash/race tests; M5 live opt-in subject to provider gates. Legacy RUNNING/ATTENTION_REQUIRED/UNKNOWN never treated as safely resumable. Rollback feature flag halts new claims but **preserves held reservations and remote evidence**, not DROP DB.

Acceptance: X01, X02, X03, X04, X05, X06, X07, X11; stress 10,000 events and 2-project/1-account race; fake-only. No claim that SQL schema has been implemented.
Decision triggers: actual multiple-project IDs, official provider policy, file-system portability, DB concurrency, migrations and security boundaries.
