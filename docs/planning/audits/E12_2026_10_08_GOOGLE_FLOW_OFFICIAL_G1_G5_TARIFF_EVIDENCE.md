# Flow-Otomatis — Official Google Flow research for G5 price and G1 policy (2026-10-08)

**Date:** 2026-10-08 WIB  • **Scope:** ASTRA / source research only  • **Status:** G5 PUBLIC EVIDENCE PARTIAL, **NOT** live PASS; G1 provider automated-multi-account permission **UNKNOWN/BLOCKED**.

## Primary evidence (opened official Google pages)

1. [S1] [Google Flow Help — Manage your Google Flow credits](https://support.google.com/flow/answer/16526234?co=GENIE.Platform%3DDesktop&hl=en). Opened 2026-10-08. Official Help text says Gemini Omni Flash **720p** generation prices, **per generation (not per request)**: 4s=7, 6s=10, 8s=12, 10s=15 credits. One request may generate multiple videos. Basic daily credit allocation is described as 50 credits, subject to account eligibility; it is NOT proof that any given signed-in account currently has 50 usable credits. See the same Help article for refresh rules and per-account remaining-credit UI.
2. [S2] [Google Flow Help — supported models and features](https://support.google.com/flow/answer/16352836?hl=en). Official page lists **Gemini Omni Flash 1.1** support for 4/6/8/10s and both aspect ratios, with 720p standard and 360p draft. Frozen project profile remains **Omni Flash 1.1 / 720p / 16:9**, never substitute 360p to save credits.
3. [S3] [Google Flow Help — getting started and eligibility](https://support.google.com/flow/answer/16353333?hl=id). Eligibility/access depends on age, region, account type/subscription and product provisions; don't assume every account can operate the same profile.
4. [S4] [Google Terms of Service](https://policies.google.com/terms?hl=id), effective July 30 2026. This source prohibits some automated access that violates machine-readable website directions. The pages reviewed do **not** expressly authorize concurrent multi-account browser mutation automation. This is a safety conclusion of **insufficient proof**, **not** a categorical statement that all automation is prohibited.

### Dated reference price table (simulation only)

| Exact generation profile | Duration | Credits per generated VIDEO | Source |
|---|---:|---:|---|
| Gemini Omni Flash 720p | 4s | 7 | S1 |
| Gemini Omni Flash 720p | 6s | 10 | S1 |
| Gemini Omni Flash 720p | 8s | 12 | S1 |
| Gemini Omni Flash 720p | 10s | 15 | S1 |

**Provider documentation inconsistency warning:** a separate stale indexed locale result for this same Help topic displayed historical 15/20/25/30 pricing. Therefore this page lookup is a **dated public quote only**. It cannot be used as the irreversible dispatch charge without verifying the latest settings of the logged-in exact account (model, resolution, duration, output count, checked-at and source). Google explicitly says that charges are subject to change and directs users to Flow prompt Settings.

## New planning implications — NO IMPLEMENTATION IN THIS PR

- Store `TariffQuote(model, resolution, duration_s, output_count, credit_per_generation, total_quote_credits, source_url, checked_at, expiry, proof_ref, profile_id)`. Immutable quote digest binds approval. No hardcoded permanent tariff.
- For each scene select 4/6/8/10 by ceiling of immutable Audio/SRT Target, not by credit optimization; reject Target >10 seconds rather than silently shortening it.
- `quote_total = credit_per_generation * output_count`; charge evidence after remote operation is separate from local reservation. **One request may produce multiple videos**; do not confuse request count with generated-video count.
- A daily allowance on Google's page **does not prove per-profile READY or remaining balance**. `credit_observed` must be fresh, verified and account-eligible; `MANUAL_SIMULATION` never dispatches.
- Reservation and quote provenance must be checked immediately before every remote mutating attempt. Stale/mismatched price, plan, selected account or output count -> `PLAN_STALE`, stop new claims and seek explicit reapproval.
- Account sign-in/consent, provider permission, verified account entitlement, real rate quote and restart READY are **separate gates**. If provider scope is UNKNOWN, multi-account automation is **disabled**; offer SIMULATION or compliant manual workflow.
- No account rotation or quota circumvention, no MFA/CAPTCHA bypass, no silently retried billed actions. Accepted/uncertain attempts stay bound to their original account and held credit until evidence-based reconciliation.

## Gate decision record

| Gate | Evidence from this review | Decision |
|---|---|---|
| Feature capability 4/6/8/10 at Omni 720p | Public official model docs S2 | **REFERENCE SUPPORTED**, not a live account proof |
| G5 nominal price schedule | S1 says 7/10/12/15 credits *per generated video* | **PARTIAL PUBLIC RESEARCH**; live account/terms/tariff snapshot still required |
| G5 actual per-account balance/reset | No account was accessed or checked | **UNVERIFIED** |
| G1 automating Flow/browser, multiple concurrent accounts | Terms S4 + help S3 do not establish authorization | **BLOCKED / UNKNOWN** |
| G4 original approved UI assets on GitHub | 22 exact V2 UI owner signoff YES; binary files absent from PR #25 | **G4 archive PENDING** |
| Strict G0; E12-01 ADR T06; G6 | Independent gates unchanged | **BLOCKED / PENDING** |

### Deliverable and handoff

A two-page Word research memo `FLOW_OTOMATIS_E12_G1_G5_SUMBER_RESMI_TARIF_DAN_KEBIJAKAN_REVIEW_2026-10-08.docx`, SHA256 `2fe054836cae9cebb3cc66064975c9ba9b1aa7f6df68f999b29c96add7915971`, was generated and visually rendered in the ChatGPT session; **this DOCX binary has not been uploaded to GitHub**. This Markdown is a record in the PR.

**STOP:** do not merge PR #25 or implement source code/migrations/browser actions, use credits, or mark G1/G5 PASS without all gates and documented permission. Existing 22 UI images are **already user-approved**; this research does NOT replace/revise their exact bytes.
