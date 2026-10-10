> **LATEST 2026-10-09 T06 ARCHITECTURE DECISION — OWNER APPROVED DESIGN.** Owner explicitly approved the six D01–D06 architecture design choices detailed in `docs/planning/step12/E12_01_T06_SIX_DECISION_OWNER_REVIEW_2026-10-09.md`; official decision record `docs/planning/decisions/E12_01_T06_OWNER_APPROVED_SIX_ARCHITECTURE_DECISIONS_2026-10-09.md`. Older `T06 PENDING` and `ADR PROPOSED` statements below refer to the pre-signoff planning snapshot and are now **superseded only for architecture design signoff**. Actual new-coordinator code/tests/migrations, provider G1/G5/G6 gates, unmerged G0 source integration and live pilot acceptance remain **NOT PASS**. All original content retained as provenance; **NO CODING / MERGE / LIVE**.

> **2026-10-09 LATEST STATUS:** This is an **8 October proposal snapshot**. The historical `C10 UI NOT STARTED`, `G4 archive PENDING` and old `G0 authority BLOCKED` statements below are superseded for those **specific subgates**: the owner accepted 22 new designs and 24/24 binary archive on **Draft PR #25**, and explicitly approved G0-A/B/C canonical source selection on **Draft PR #27** (six original planning DOCX 6/6 archived). **T06 D01–D06 CONTENT is still PENDING; no architecture/adoption/coding authorization.** Latest six-decision cross-module review: `docs/planning/step12/E12_01_T06_SIX_DECISION_OWNER_REVIEW_2026-10-09.md`. G1/G5/G6 and overall pre-code integration remain blocked/pending. All referenced PRs remain unmerged.

# E12-01 — ASTRA Architecture Decision Matrix / Handoff
**State: PLANNING PACKAGE PREPARED / ADR-020–023 PROPOSED. NOT APPROVED FOR CODING.**
Repository `inoriko920-dev/Flow-Otomatis`; reference main before planning `978dbb31ce2024da0c70280f260f421e2687382b`. Scope: E12-01 ONLY, no source/UI/schema/browser mutation.

## Decision matrix
| Decision | Proposed conclusion | Owner / status | Gate |
|---|---|---|---|
| C01 ledger/reservation authority | One global SQLite coordinator, project DB projections | ADR-020 / PROPOSED | G0/G3 |
| C02 2-DB consistency | Commit global before outbox projection; idempotent replay | ADR-020 / PROPOSED | G3 |
| C03 DB location | `PathService.settings_root/coordination/` candidate | ADR-020 / NEEDS REVIEW | G3 |
| C04 identifier scoping | opaque stable project_id + scene_id + revision and attempt_id | ADR-020 / NEEDS REVIEW | G3 |
| C05 account entitlement | only user-opt-in + verified provider policy/capability | ADR-021 / G1 BLOCKED | G1/G5 |
| C06 credit snapshot | observed fresh provider proof; manual balances simulation only | ADR-021 / PROPOSED | G5 |
| C07 submit boundary | durable SUBMIT_STARTED before browser mutation; UNKNOWN hold | ADR-022 / PROPOSED | G3/G7 |
| C08 legacy jobs | versioned adapter; preserve per-project schema v2/history | ADR-022 / PROPOSED | G3 |
| C09 worker ownership | per-profile actor + single process/global coordinator lock | ADR-023 / PROPOSED | G1/G9 |
| C10 app UI | preserve 30 frozen compositions; new dialog design E12-02 STOP gate | UI addendum / NOT STARTED | G4 |
| C11 browser live | current selectors/provider approval unknown; no mutation | G1 + I12-01 / BLOCKED | G1/G6 |
| C12 migration/rollback | create-only, backup, compatibility and no-loss tests | ADR-020,022 / PROPOSED | G3 |

## Existing canonical owners and no-duplicate search
- `domain/job/model.py` existing QUEUED etc; coordinator status is separate projection.
- `application/ports/generation_jobs.py`, `generation_provider.py`, `generated_media_download.py` are existing typed boundaries; do not add duplicate providers if an adapter suffices.
- `application/services/local_generation_queue.py` serial safety should remain; optional future account-aware orchestration sits behind a feature flag.
- `infrastructure/persistence/sqlite_generation_job_repository.py` schema v2 and lease guards should remain compatible; global coordinator is distinct, not a wholesale replacement.
- `workers/browser/google_flow_generation.py`, `google_flow_download.py`, `google_session_worker.py` are browser owners; live selector drivers are not yet implemented.
- `infrastructure/filesystem/path_service.py` provides global Settings root; `bootstrap/main.py` composition only.
- `presentation/` cannot import SQLite/Playwright; new UI needs E12-02 images and consolidated reference DOCX.

## Draft DTOs, no executable implementation
```text
CreditSnapshot(profile_id, observed_balance?, source, observed_at, expires_at, eligibility, evidence_id)
TariffQuote(price_version, model, resolution, flow_duration_s, output_count, cost_credits, evidence_id)
FrozenPlan(plan_id, project_id, revision, source_digest, assignment_digest, budget_cap, approved_at?)
Attempt(attempt_id, project_id, scene_id, revision, profile_id, fencing_epoch, request_digest, state)
WorkTicket(attempt_id, profile_id, fencing_epoch, plan_revision, request_digest, max_cost, expires_at)
OutboxEvent(event_id, attempt_id, topic, payload_digest, acknowledged_at?)
```

## E12-01 ordered task cards (ASTRA only)
1. T01 — Confirm coordinator scope and credit invariants in ADR-020. Evidence: X01 two projects/1 account, no duplicate reservation.
2. T02 — Record identity, terms, consent and credit-evidence boundaries ADR-021. Evidence: unknown eligibility or manual balance never enables live.
3. T03 — Record create-only migration/safe rollback, versioned schemas, outbox. Evidence: crash M0-M5, legacy schema v2 intact.
4. T04 — Approve transition diagram and ambiguous submit logic ADR-022. Evidence: exactly one irreversible submit boundary, never retry UNKNOWN.
5. T05 — Approve per-profile actor/scheduler scope ADR-023. Evidence: 2-fake-profile race/fencing and single-worker profile ownership.
6. T06 — Cross-module ASTRA review + owner signoff, register approval dates and acceptance results. **PENDING**, not automatically satisfied by "lanjutkan".

## Acceptance / DoR
| Test | Scenario | Mandatory safe result |
|---|---|---|
| X01 | 2 projects share 20 observed credits, both ask 15 | at most one reservation commit |
| X02 | 2 workers same scene | one active claim |
| X03 | stale/manual balance | 0 provider submits |
| X04 | stale fencing token | all stale writes rejected |
| X05 | crash global commit before project projection | idempotent outbox replay |
| X06 | crash after SUBMIT_STARTED, no stable result ID | ATTENTION, held credit, no duplicate Generate |
| X07 | changed price/source/revision | plan invalidated & new approval |
| X08 | wrong-account remote ID | refuse access/download |
| X09 | download collision | preserve existing file |
| X10 | DB update failure after file publish | manual reconcile, no overwrite |
| X11 | 10,000 ledger events/race | no double reservation or ledger duplicates |
| X12 | unsupported account capability | 0 live dispatch |
| X13 | quit/restart while uncertain | preserve evidence, no auto retry |
| X14 | policy prohibits/unknown multi-account | 0 multi-profile mutating actions |
| X15 | log/profile/ZIP export check | no secrets |

G0 original DOCX visual-authority parity remains BLOCKED as recorded in `PROJECT_STATE.md`; G1 live provider compliance UNKNOWN; G5 actual credits UNKNOWN; G6 restart READY proof UNKNOWN. This does NOT block ASTRA from preparing proposals, but **blocks SOL code / UI / migration / live**.

## Required next handoff
- Do NOT execute E12-02 UI design prompt prematurely or code from draft ADRs.
- If owner explicitly approves this architecture package, record ADR statuses and re-check G0, then E12-02 prompts; at the E12-02 prompt-complete checkpoint STOP until all new UI images are reviewed and consolidated in one DOCX.
- Read docs `PROJECT_STATE.md`, `TASKS.md`, `docs/planning/SOURCE_OF_TRUTH_MANIFEST.md`, frozen UI ref + overrides, and this packet; verify main SHA before editing.
- Report exact Git commit, tests actually run, blocked gates, and next wave in each handoff.
