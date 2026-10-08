# ADR-021 — Profile Consent, Provider Policy and Credit Evidence (E12-01)
Status: **PROPOSED / PROVIDER POLICY G1 NOT VERIFIED** • 8 Oct 2026 WIB • Baseline: `978dbb31ce2024da0c70280f260f421e2687382b`
Relates to ADR-017, I12-01 normal Chrome login, ADR-020, frozen Omni Flash 1.1 / 720p / 16:9 project profile.

## Principle
Only accounts the user legitimately controls and opted into may be represented. **No automated account rotation to evade account quotas, free-tier restrictions, anti-abuse systems or access controls.** Multi-account concurrent live use is conditional on provider authorization and proof of per-account eligibility; otherwise simulate credit plans and require compliant manual/official integration.

## Identity / consent contract (proposed)
`profile_id: UUID` immutable local opaque ID; `account_fingerprint`: redacted/nonsecret local identity proof only when appropriate; `label`: display alias; `authorized_by_owner_at`; `policy_evidence_ref`; `policy_scope` in {UNKNOWN, MANUAL_ONLY, OFFICIAL_API, AUTOMATION_VERIFIED, FORBIDDEN}; `session_status`; `restart_gate_status` (**historical observation; not persistent READY authorization**); `model_eligibility`; `last_verified_at`; `profile_concurrency_cap`.
- Never use email/phone/account name as primary key or export identity. Do not store cookies, Chrome profiles, passwords, OAuth tokens or MFA recovery data in Git.
- Manual normal Chrome sign-in, MFA/CAPTCHA handled by human. Browser attach only after authentication, consistent with ADR-017. A profile starts each **fresh application process** in a non-READY state until that process independently verifies the existing Chrome session and the exact account identity. Persisted READY/restart proof is **historical audit evidence only**, never a reusable capability token. Verified account session is still separate from owner consent, provider policy and tariff entitlement; none follows automatically from successful sign-in.
- A profile never borrows another's session/remote_result_id. A different profile cannot redownload a result of account A.

## Credit and tariff evidence
`CreditSnapshot {profile_id, balance: int | null, observed_at, expires_at, source, proof_ref, entitlement}`; `TariffQuote {model, resolution, seconds, output_count, credit_cost, source_url, checked_at, version}`.
- Source types: `PROVIDER_OBSERVED`, `MANUAL_SIMULATION`, `UNKNOWN`. Only fresh provider-observed balances with reliable service entitlement can enable *eligible* auto-dispatch. Snapshot TTL is configurable and **must be measured/approved**; no arbitrary perpetual freshness.
- Current online tariff information and product capabilities can change; model cost 4/6/8/10 shown in an older plan is a reference **not a guaranteed billing contract**. Verify actual UI/provider source and number of generated variants immediately before budget approval and submit; never claim credit spent from a local estimate.
- External spend since last observation -> wait/requote. User-selected max total and per-account budget are hard ceilings; no silent retry billed actions. Unknown price/capability is a hard stop for live.
- Preserved frozen app profile: Omni Flash 1.1, 720p, 16:9 and duration choices 4,6,8,10. If account cannot run this exact profile, block. No silent substitute/upgrade.

## Provider authorization gate
Prior to any live web automation, record **reviewed Terms/product guidance**, platform-approved means of access, legitimacy of intended action, data usage limits, and whether concurrent signed-in profiles are permitted. A generic sign-in or technical ability to attach CDP does NOT imply permission. If authorization cannot be established: no browser mutating action; offer manual workflow or approved API. No anti-bot evasion, MFA bypass, proxy hopping or hidden rate-limit circumvention.

Acceptance: X03 (stale/manual balance), X07 (changed quote), X08 (wrong profile result), X12 (wrong entitlement), X14 (policy disabled), X15 (sensitive log check) plus explicit deny-by-default.
Open review questions: actual provider scope, account/region entitlements, evidence freshness, number of outputs, reset boundary and tariff provenance. No live policy PASS claimed here.
