# ADR-023 — Account-Aware Scheduler and Browser Actor Isolation (E12-01)
Status: **PROPOSED / LIVE PARALLELISM BLOCKED** • 8 Oct 2026 WIB • Baseline: `978dbb31ce2024da0c70280f260f421e2687382b`
Related: ADR-005 existing serial R1 queue, ADR-017 Browser Worker ownership, ADR-020 global authority, ADR-021 policy.

## Scope and alternatives
Legacy `LocalGenerationQueueService.run_until_idle()` is serial; `SqliteGenerationJobRepository.claim_next()` checks a blocking RUNNING/ATTENTION_REQUIRED state for the entire episode. Do NOT weaken these guards directly in place. Introduce a separate versioned coordinator/port behind feature flag, while legacy serial mode remains intact until fake regression + authorized pilot gates PASS.

## Scheduling contract
- Plan immutable `WorkTicket {attempt_id, project_id, scene_id, plan_revision, profile_id, lease_epoch, request_fingerprint, max_credit, issued_at, expiry}`.
- Deterministic allocator assigns scene to an opted-in, READY, policy-eligible account whose **fresh available credit** and capabilities cover the precise approved quote. Dry run may use manually entered balances but always labels simulation, and cannot dispatch.
- User reviews a full project plan (assignments, credits per duration/output, total/per-account budget, skipped scenes, buffer) and approves its digest. Replanning changes revision and requires new approval.
- One in-flight mutating submit per eligible profile/actor; many profiles may work on **different** scenes only when Google explicitly permits concurrent use. No concurrency assumed from login count. Cap starts at one in fake tests, then two synthetic profiles, then limited live test after G1/G6–G9 gates.
- Scheduler checks feature flag, global app owner lock, account lease, credit reservation, provider policy, credentials/session and input fingerprint **again** immediately before handoff. Final worker gate must confirm same immutable attempt and fence.
- Pause prevents new claims without claiming it cancels an ambiguous click. Graceful stop drains pre-mutation tasks; in-flight uncertainty enters attention. Fairness/starvation heuristics must be tested and deterministic, not improvised.

## Browser actor model
All Chrome/CDP/Playwright handles reside within the account's dedicated worker execution owner. Qt main thread never holds those objects or SQLite handles. Interactions pass sanitized application DTO/events. Human login/MFA only in normal installed Chrome; automation after sign-in and permitted policy only. Do not attach more than one actor to the same account/browser profile.
Browser actor lifecycle states: `DISCONNECTED -> HUMAN_AUTH_PENDING -> READY_VERIFIED -> BUSY -> READY_VERIFIED`, with `AUTH_REQUIRED/ATTENTION/SHUTDOWN` branches. Restart-ready proof persisted without secrets; it is not a proxy for live provider permission.
- Stable remote ID must bind exact account+attempt and remain invisible to other profile actor except sanitized aggregate UI; prevent cross-account remote download.
- Periodic health checks never stealth sign-in, never bypass challenges or continuously retry blocked actions.

## Simulation, QA and rollout
Phase A: 1 fake account serial compatibility. Phase B: two synthetic profiles, same account contention, cross-project credit race. Phase C: worker crash/restart, stale fencing, paused queue, mixed durations 4/6/8/10, 60-scene fake load. Phase D: *if G1/G5/G6/G7/G8 PASS and explicitly consented* one live authorized account/scene; Phase E: only after separate G9 authorization/acceptance, live two-account scenario. Any policy UNKNOWN => no live.
Acceptance X01/X02/X04/X08/X09/X10/X11/X12/X14, UI frozen 30/30 visual regression unchanged; 10k ledger event and 60-scene soak targets. Live flow driver and selectors NOT implemented by this ADR.
