# E12-01 T06 — OWNER-APPROVED six architecture design decisions (D01–D06)

**Project:** `inoriko920-dev/Flow-Otomatis`  
**Decision date:** **2026-10-09 WIB**  
**Decision category:** **Architecture DESIGN approved; NOT production-code/merge/live authorization**  
**Scope:** Draft PR #26 only, frozen architecture references ADR-020–ADR-023. No code, database migration, Google Flow account access, Generate/Download, credits, or PR merge authorized by this approval.

## 1. Exact owner signoff and what it means

In the current conversation, the assistant presented a six-row T06 owner review describing **D01 ledger, D02 identity, D03 account consent and provider credits, D04 uncertain submit recovery, D05 account/browser actor isolation, D06 safe opt-in migration and fake tests**, and explicitly asked: **"Apakah kamu menyetujui keputusan D01–D06 sebagai rancangan arsitektur final? Persetujuan ini hanya untuk rencana; coding, penggunaan kredit, dan otomatisasi Google Flow tetap menunggu seluruh gate lainnya PASS."** The owner answered **`setuju`**.

This is **EXPLICIT PASS for T06 D01–D06 architecture design and owner signoff**, not for operational prerequisites, implementation, testing, merge, provider authorization, or the original Master Plan's separate start-coding approval. It is distinct from the owner's earlier `setuju` for G0 original source/reference selection.

Authoritative detailed owner-review contract (approved *as a design*, unchanged frozen content):
`docs/planning/step12/E12_01_T06_SIX_DECISION_OWNER_REVIEW_2026-10-09.md`

## 2. Six accepted design choices

| ID | Owner-approved design | Hard limits and acceptance evidence still required |
|---|---|---|
| **D01 — Global credit authority** | Use one **local, single-device SQLite coordinator** to own reservations, attempts, holds, leases and ledger events. Existing per-project schema-v2 stores remain authoritative for imported scenes/media/history; sync via idempotent outbox, **not** an asserted cross-database ACID transaction. | Concurrency, crash and projection tests unrun; no new SQLite coordinator created. |
| **D02 — Immutable identity and fencing** | Stable opaque project/scene/approved-plan revision/attempt identity, unique credit reservation, atomic fencing under short transaction; hold SQL lock only for local work, **never across browser interaction**. | Global project key, coordinator settings-root folder and migration details remain implementation-review subjects; prove 2-project/1-account atomicity and stale worker denial. |
| **D03 — Provider permission and credit provenance** | Per-account owner consent, exact model entitlement, **fresh provider-observed** per-account available credit and tariff/outputs/approved budget required for real dispatch. Manual values are explicitly **simulation only**. | G1 provider Terms/automation permission **UNKNOWN/BLOCKED**, G5 per-account evidence **UNVERIFIED**. No quota evasion, silent account rotation, unapproved parallel mutating browsers or free-tier bypass. |
| **D04 — Durable submit ambiguity** | Persist `SUBMIT_STARTED` before any provider mutation. Unknown external result is `SUBMIT_UNCERTAIN` with original-account credit HELD and read-only reconciliation, **no automatic retry or account reassignment**. `FAILED_SAFE` only with conclusive account-bound evidence that the provider accepted no chargeable submit. | A timeout, missing result ID, browser crash, restart or disconnected session is **not** evidence of failure-safe. All fake ambiguity test cases unrun; legacy status enum unchanged. |
| **D05 — Profile actors and fresh READY** | One worker/browser actor per explicitly eligible profile, one global coordinator app writer. Every fresh application process starts non-READY until it independently checks correct current Chrome session, identity and worker ownership. | Persisted READY is historical only. G6 restart proof **UNVERIFIED**. Live multi-account parallelism needs provider G1 and separate G9 signoff, **not** granted here. |
| **D06 — Safe compatibility rollout** | Feature-flagged/create-only coordinator, backup and preserve legacy project DB/schema/history, versioned adapter, idempotent outbox, rollback that **retains** uncertain attempts/reservations, plus fake-only crash/race/security/UI acceptance first. | No schema migration, coordinator coding, fake test execution, 60-scene/10k-event claims or release authorized by T06 design approval. |

Reference constraints: frozen original 30-PNG UI Word and unchanged `docs/ui/IMPLEMENTATION_OVERRIDES.md` remain authoritative (G0 owner-approved on Draft PR #27); new 22 owner-approved E12-02 images and final DOCX on Draft PR #25 supplement those references. Omni Flash 1.1 / 720p / 16:9, Flow candidate durations 4/6/8/10s, distinct Generate and Download phases, human login/MFA, and scene mapping remain unchanged.

## 3. Status interpretation / gate ledger

| Scope | Status after this exact approval | Meaning |
|---|---|---|
| **T06 D01–D06 decision-content and owner signoff** | **PASS / OWNER APPROVED (design only)** | ADR-020/021/022/023 may be labeled **accepted architecture design** without claiming they are implemented or live-permitted. |
| G0-A/B/C original reference selection | **PASS / owner approved** | Canonical 30 UI original DOCX, E12-00 15:21, original Master V1.1 and ADR E12-01 V1.1 *review* source selected. |
| G4 22 approved UI + final/original DOCX preservation | **PASS / 24/24 GitHub** | Assets preserved in unmerged Draft PR #25. |
| G0 original planning binaries | **PASS / 6/6 GitHub** | Preserved in unmerged Draft PR #27. |
| **Overall G0 repository integration / all pre-code prerequisites** | **NOT YET PASS** | Design/reference files are on separate **unmerged review branches**, not effective merged baseline; no source-of-truth integration signoff for implementation. |
| **G1 provider authorization** | **UNKNOWN/BLOCKED** | Google Flow policy and multi-account/automated browser permissions are not established. |
| **G5 current account-specific tariff, credit and entitlement** | **UNVERIFIED** | Public price reference is not a real per-account grant or allowed spend. |
| **G6 valid READY after full restart** | **UNVERIFIED** | Human login alone or stored historical READY does not prove current-session authority. |
| G3/G7/G8/G9 implementation/test/pilot gates | **NOT PASS for new coordinator** | The X01–X15, F01/F02 and M0–M5 fake acceptance matrix is **planned**, **not run**. |

**Even when the architecture is approved, the actual build remains prohibited** under existing governance until all independent pre-code gates are PASS and owner gives the required distinct implementation authorization. Likewise, there is **no permission to merge PR #25, PR #26 or PR #27** based solely on this design approval.

## 4. What may be done next

1. Keep PR #26 **DRAFT**; update ADR status headings and source-of-truth Markdown **in the review branch** to reflect approval, preserving original decision/test requirements.
2. Perform documentation-only policy and provider eligibility research for G1 and document precisely what is **provably permitted**, **not verified**, or **forbidden**; fail closed, no sign-in or live browser mutations.
3. Plan non-invasive manual G6 per-account restart verification and G5 quote evidence for when the user chooses to supply them; avoid demanding passwords, session cookies, token exports or private credentials.
4. Only after independent G0/G1/G3/G5/G6/G7/G8/G9 gates and explicit start authority may SOL be handed implementation tasks; first stage must be fake-only and backward compatible.

**APPROVED: ARCHITECTURE DESIGN ONLY. NOT APPROVED: CODING, MIGRATION, MERGE, REAL PROVIDER ACTIONS OR CREDIT USE.**
