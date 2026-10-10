# Flow-Otomatis — E12-01 T06 preflight of ADR-020–023

**Date:** 2026-10-08 WIB  
**Status:** **REVIEW PREPARED — ADR T06 OWNER SIGNOFF STILL PENDING**. Only cross-document consistency review, not implementation or policy approval.

### Inputs reviewed from `main`

- `docs/architecture/ADR-020-global-credit-and-attempt-authority.md`
- `docs/architecture/ADR-021-profile-consent-and-credit-evidence.md`
- `docs/architecture/ADR-022-ambiguous-submit-state-and-recovery.md`
- `docs/architecture/ADR-023-per-profile-scheduler-and-actor-isolation.md`
- `docs/planning/step12/E12_01_ADR_DECISION_MATRIX_AND_HANDOFF_2026-10-08.md`

### Review evidence and limits

The cross-ADR proposal is internally broadly aligned on one global credit coordinator, no two-DB ACID claims, conservative durable `SUBMIT_STARTED` before external action, held reservations on uncertainty, account-isolated actors and provider-permission gate. **No production implementation is implied by these words.**

The ChatGPT conversation has newly generated the **four-page** DOCX `FLOW_OTOMATIS_E12_01_T06_PREFLIGHT_ADR_REVIEW_BELUM_DISETUJUI_2026-10-08.docx` (SHA256 `604d3c4caaefd1c63c25d7581983fabdcc8f7ac18e377e38626f3a03db0a3278`) plus a TXT summary bundled in `FLOW_OTOMATIS_E12_01_T06_PREFLIGHT_REVIEW_ONLY_2026-10-08.zip` (SHA256 `64986b9e0b8729636248b3a34e2c5634868cd6df3c41d6195dd9bc4b461a4c59`, ZIP CRC PASS). **These binaries are downloadable conversation artifacts, NOT uploaded to GitHub.** The 4 Word pages were rendered and visually QA checked.

### Findings / proposed corrections (none approved yet)

| ID | Priority | Exact issue | Proposed safe decision |
|---|---|---|---|
| F01 | P1 | ADR-022 transition text calls terminal no-acceptance state `SAFE_FAILURE`, but recovery text calls it `FAILED_SAFE`. | Choose one canonical enum (proposed `FAILED_SAFE`) and one explicit proof-required transition, before data schema/migration code. |
| F02 | P1 | Persisted restart proof could mistakenly be treated as permanently authoritative READY in ADR-021/023. | Store audit evidence only; re-verify actual READY after each full app restart, separately from provider policy and owner consent. |
| F03 | P1 | Observed credit and tariff snapshot TTL, actual eligibility and evidence not authorized. | Unknown/stale/manual => simulation only, no live dispatch. Approve proof sources/expiry and account capability first. |
| F04 | P1 | G0 strict historical DOCX authority and G4 uploaded binary evidence remain incomplete. | STOP code despite 22/22 V2 UI visuals being explicitly approved. |
| F05 | P2 | Coordinator DB path, opaque stable project ID, migration/rollback/fencing protocol need final decisions/tests. | Conclude C01–C04 and X01/X02/X04/X05/X11 fake crash/race tests before coding. |
| F06 | P2 | Manual Google sign-in, user ownership and provider live automation permission are independent. | Separate and default-deny gates for these proofs, never infer permission from account READY or available balance. |

### T06 human decisions D01–D06 — all PENDING

1. **D01** Coordinator authority and per-project outbox projection: accept target architecture only after strict G0/G3 review.
2. **D02** Durable identity, SQLite coordinator path and migration/backup guarantees: sign off after acceptance test plan.
3. **D03** Normalize failed-safe enum and ambiguous-submit recovery without silent resend/account rotation.
4. **D04** Provider consent, eligibility, credit/tariff evidence, expiration and official supported automation scope.
5. **D05** Per-profile Chrome actor isolation and fresh READY proof after every restart.
6. **D06** Explicitly prohibit coding until all independent implementation gates and factory handoff conditions PASS.

### Test and gate checklist

**Fake test evidence required before live:** X01–X15 (shared credit race, same-scene concurrent claim, stale prices, fencing, outbox idempotency, uncertain submit crash/restart, cross-account result isolation, no-clobber output, immutable ledger, policy deny-default, secret-free logs).

**Statuses:** UI E12-02 owner visual signoff **PASS**; GitHub PNG/DOCX binary archive G4 **PENDING** (PR #25 still has 0/24 approved source binaries); G0 **BLOCKED**; ADR T06 **PENDING**; G1/G5/G6 **UNVERIFIED**, G3 architecture/migrations proposed. **NO CODE / MERGE / REAL GENERATE / CREDIT SPEND**.

The latest V2 Windows Git upload kit is still local and requires authenticated execution on a machine with the files. Do not misrepresent successful local rehearsals as a remote GitHub push.
