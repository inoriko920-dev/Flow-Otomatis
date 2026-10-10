> **LATEST 2026-10-09 — OWNER-APPROVED ARCHITECTURE DESIGN (D01–D06) / IMPLEMENTATION STILL BLOCKED.** After the original review below was authored, the owner was explicitly asked to approve **D01–D06 as final architecture design only** and replied **`setuju`**. The signed decision record is `docs/planning/decisions/E12_01_T06_OWNER_APPROVED_SIX_ARCHITECTURE_DECISIONS_2026-10-09.md`. Read all historical `T06 decision PENDING`, `ADRs PROPOSED`, and `not owner approved` wording below as **superseded for T06 design signoff only**; tests and live gates remain unexecuted/unverified. Architecture D01–D06 **PASS (decision only)**. G0 source-choice PASS but repository-integration precode gate not complete; G1 UNKNOWN/BLOCKED, G5 and G6 UNVERIFIED, G3/G7/G8/G9 not PASS. **NO CODE, MIGRATIONS, MERGE, LIVE GENERATE/DOWNLOAD OR CREDIT USE.**

# Flow-Otomatis — E12-01 T06 six architecture decisions for owner review

**Date:** 2026-10-09 WIB. **State: ASTRA REVIEW READY / OWNER T06 DECISION PENDING.**  
**Repository:** `inoriko920-dev/Flow-Otomatis`, Draft **PR #26**, docs-only, no merge and no production code. The 2026-10-09 owner reply `setuju` explicitly approved **G0 original-source/reference selection only** — it did **not** adopt these ADR architecture contracts.

## 0. Evidence, superseded status, and what actually exists

- **G0 source authority G0-A/B/C: owner APPROVED** in Draft PR #27 decision `docs/planning/decisions/G0_2026_10_09_OWNER_APPROVAL_OF_CANONICAL_REFERENCES.md`. The accepted primary E12-01 planning reference is the original 54,229-byte `E12_01_ASTRA_ARCHITECTURE_ADR_V1_1_GITHUB_REVIEW_2026-10-08.docx` on PR #27. The original Master Plan V1.1 and E12-00 15:21 handoff are also there; physical six-DOCX archival **6/6 PASS**.
- **G4 approved UI archival: 24/24 PASS** on Draft PR #25. 22 new V2 screens were owner-approved. The 30 original uncompressed PNG UI Word is now owner-selected as visual authority. The smaller 30-JPEG Word on main is historical preview, not proven equivalent. Respect existing `docs/ui/IMPLEMENTATION_OVERRIDES.md`.
- **CI latest PR #25/#26/#27 was SUCCESS before this review commit**; any newly authored docs must receive fresh CI. All three PRs remain DRAFT/unmerged and `main` has not incorporated their reference binaries yet.
- Existing `main` implementation genuinely has `src/flow_otomatis/application/services/local_generation_queue.py` (serial queue), `infrastructure/persistence/sqlite_generation_job_repository.py` (project schema v2, lease and `ATTENTION_REQUIRED`), `application/ports/generation_jobs.py`, and `infrastructure/filesystem/path_service.py`. This review only inspected existing owners, **did not implement the new coordinator**.
- **Correct outdated text in earlier E12-01 decision matrix:** `C10 UI addendum NOT STARTED` and `G4 archive PENDING` were historically true during planning, but are superseded: E12-02 22 images are signed off and the approved binary archive exists on PR #25 (**G4 archival PASS**). This still does not establish coding authorization or cross-PR merge.
- ADRs `ADR-020` through `ADR-023` are all still **PROPOSED**. PR #26 earlier corrected ambiguous `SAFE_FAILURE` to **`FAILED_SAFE`** and clarified post-restart session READY is **not persisted authorization**.

## 1. Exactly six T06 architecture decisions to be approved separately

| ID | Proposed owner decision | Existing source/why | Conditions/limits |
|---|---|---|---|
| **D01** | One **local global SQLite coordination ledger** for credit reservations, attempts, leases and immutable events; project SQLite remains source for scenes/media and legacy job history. | ADR-020; prevents 2 projects reserving the same account credit. | Explicit single-device scope; no network-share/multi-device guarantees; global commit then idempotent outbox projection, **not** cross-DB ACID. |
| **D02** | Immutable work identity: stable opaque `project_id + scene_id + approved_plan_revision + attempt_id`; reservations and claims are unique, fenced and atomic. | ADR-020/022/023; existing `episode_id` may not identify a workspace globally. | DB path under `PathService.settings_root / coordination` remains proposed implementation detail; migrations require independent review; no duplicate scene/account submit. |
| **D03** | Each profile requires owner opt-in, provider-permitted access, exact model entitlement, fresh **provider-observed** credit and approved tariff/budget; manual numbers enable only labeled simulation. | ADR-021 and G1/G5. | Provider Terms/capability proof remains **UNKNOWN/BLOCKED**. Account rotation to evade quotas and unapproved live parallelism are prohibited. No live dispatch from a proposed ADR. |
| **D04** | Durable `SUBMIT_STARTED` recorded before browser mutation; unknown remote outcome becomes `SUBMIT_UNCERTAIN` with held reservation and **read-only** reconciliation. `FAILED_SAFE` requires conclusive provider/account-bound proof no chargeable submit was accepted. | ADR-022; PR #26 terminology fix. | Timeout, no result ID, restart, stale UI and browser disconnect cannot mean safe failure; no blind retry, scene reassignment or account-switch after ambiguity. Legacy project enum remains unchanged. |
| **D05** | One browser actor per authorized profile, one global app owner/process writer; all accounts start **non-READY after full app restart**, then must verify current session+correct identity+worker ownership. | ADR-021/023; F02 review. | Historical READY is audit only; valid login does **not** imply provider policy, credit entitlement or spend permission. Per-account live parallelism only after separate G1/G9 evidence and owner consent. |
| **D06** | Non-destructive, feature-flagged integration: create-only coordinator DB, backup existing project DB, compatibility adapter and idempotent outbox; rollback stops new claims but never drops holds/history. **Fake-only acceptance tests first**. | ADR-020/022/023; existing schema v2 and UI/Windows packaging. | No schema migration/code by T06 text approval alone. Prove crash/race/fencing, original UI 30/30, 22 extensions, and 60-scene simulation; staged live testing separately gated. |

**Recommended ASTRA position:** all D01–D06 are internally coherent *as a prospective architecture*, with external-policy claims deliberately excluded. The **decision package is ready for owner consideration but NOT OWNER-APPROVED**, and no code/test results are implied.

## 2. Explicit cross-module contract / hard STOPs

1. **Single coordinator authority**: use short `BEGIN IMMEDIATE` transaction for attempt uniqueness and credit reservation; release SQL lock before any browser interaction. Global -> project projection uses transactional outbox with unique event IDs and at-least-once replay; never claim a two-DB atomic transaction.
2. **Stale work never spends**: immutable plan and input/image/target SHA digest, account fingerprint, tariff version, owner cap, lease epoch and policy/READY proof must be rechecked immediately before worker submit. A stale/expired or conflicting fact means DENY.
3. **Conservative remote mutation boundary**: `SUBMIT_STARTED` persisted before click. `SUBMIT_UNCERTAIN` holds exactly the original account+attempt reservation until valid account-bound reconciliation; no auto-retry/switch. `FAILED_SAFE` only after affirmative evidence.
4. **Credit provenance**: provider-observed snapshots with TTL + source/capability + exact output count; *manually entered remaining credits or assumed 50/day are simulation-only*. Public tariffs (even if published) do not prove what the account will be charged; re-check before approved plan and dispatch.
5. **Human authority**: profile opt-in and credentials/session permission are separate; provider automation policy remains G1 UNKNOWN, hence deny live submit/download mutations.
6. **UI frozen**: original 30 PNG reference + written overrides govern old UI, 22 approved new references govern addenda. No silent menu additions, fixed names, resolution/model changes or implicit Generate=Download.
7. **Crash recovery**: after any ambiguous click/commit, persist hold/evidence and show ATTENTION. Do not erase remote evidence during rollback; project DB remains readable under legacy schema v2.
8. **Security**: no cookies, tokens, emails/phone identifiers or Chrome profile secrets in SQLite debug exports, Git repository or logs; owned opaque profile IDs, redacted audit traces only.

## 3. Required acceptance matrix (not executed; future fake/sandbox tests)

| Group | Test IDs / scenario | Required PASS evidence |
|---|---|---|
| Credit atomicity | X01 two projects and one account with 20 eligible credits, concurrent 15+15 requests; X11 10,000 ledger events | **At most one** credit reservation; no duplicate ledger/outbox event; crash-safe replay |
| Attempt/identity | X02 same scene in two workers; X04 stale fence; X08 wrong-account remote result | One active attempt, stale writer rejected, other account cannot query/download result |
| Eligibility | X03 manual/stale balance, X07 changed quote, X12 unsupported exact model, X14 provider policy UNKNOWN/forbidden | **Zero live dispatch**; plan invalidated on tariff/input/profile change; manual-only simulation clearly labeled |
| Submit uncertainty | X05 global commit before project projection, X06 crash after `SUBMIT_STARTED`, X13 restart while unknown | Read-only replay/reconciliation, hold remains, **zero duplicate Generate** |
| Durable download | X09 file collision, X10 DB failure after file published | Existing file/history preserved; checksum and manual reconciliation, no clobber/delete |
| QA/security | X15 sensitive export, F01-T1/T2/T3, F02-T1..T4, 60-scene fake soak | No secrets, only canonical `FAILED_SAFE`, restart non-READY, deterministic assignment, UI 30/30 unchanged |
| Migration | M0–M5 staged creation, backup, old schema v2/history and rollback | Additive only, no legacy data loss, post-crash recovery, feature flag OFF behavior identical |

**Important:** this table specifies **future tests, not tests run**. CI passing on existing draft docs does **not** prove these proposed coordinator contracts are implemented.

## 4. Gate matrix and owner signoff distinction

| Gate | Latest actual status | Consequence |
|---|---|---|
| G0-A/B/C canonical source selection | **APPROVED** by owner 2026-10-09; binary archival on PR #25/#27 PASS | Reference choice settled; still **unmerged review branches**, overall pre-code integration not automatically PASS |
| G4 approved UI binary archive | **PASS** (24/24) | No more image generation/ZIP upload requested |
| T06 D01–D06 architecture content | **PENDING separate explicit owner approval** | ADRs stay PROPOSED; NO new code |
| G1 provider multi-account automation permission | **UNKNOWN/BLOCKED** | No live account rotation/parallel Generate/Download automation |
| G5 current account-specific balance/quote/eligibility | **UNVERIFIED** | Simulation only; no account spending |
| G6 READY after full app restart for the same account | **UNVERIFIED** | No fresh live submit |
| G3 migration/testing; G7/G8/G9 security/integration/live stages | **NOT EXECUTED for this proposed new coordinator** | No schema creation or browser mutation |

**STOP if:** user says only `lanjutkan`; that is **not** specific consent to D01–D06. Owner must explicitly accept the architecture decisions separate from G0 source approval. Even T06 owner acceptance **cannot waive G1/G5/G6 or authorize coding** while any pre-code gate remains blocked.

## 5. Proposed next handoff

1. Review D01–D06 and obtain explicit owner signoff **only for the architecture design**, if desired.
2. If approved, record owner date/decision in ADR-020..023 (approved planning, **still NOT CODE-READY**), preserve original Word + approved UI, and recheck gate matrix. Before any code require all independent pre-code gates and explicit start authority.
3. If provider automation is unapproved, retain **manual/official API workflow** and fake credit planning; do not implement quota evasion or parallel live browsers.

## 6. DOCX handoff (rendered, local conversation artifact, not yet archived in PR)

Companion Word file `FLOW_OTOMATIS_T06_REVIEW_6_KEPUTUSAN_ARSITEKTUR_2026-10-09.docx` was generated for a detailed 8-page handoff in the ChatGPT working environment. **File size 44,358 bytes**, **SHA-256 `f973968f262597aa6b19065c6709072bd900125de2fcccb0c8fc7cd6ff208c88`**. Valid OOXML/ZIP CRC **PASS**; all **D01–D06** section headings present; rendered to eight page images and visually checked for table/layout clipping. The DOCX reflects this Markdown's six proposed decisions, test plans, and STOP conditions, but it is **a separately authored companion**, not claimed byte-identical text nor uploaded to GitHub. **Do not call its GitHub archival complete until the exact DOCX is present as a verified Git blob.** The existing original E12-01 V1.1 DOCX is already preserved in Draft PR #27, independently of this new review note.
