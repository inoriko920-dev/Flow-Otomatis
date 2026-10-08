# E12-01 T06 — ADR errata + fake acceptance contract (REVIEW ONLY)

Date: **2026-10-08 WIB**. Branch: `docs/e12-01-t06-safety-clarifications-20261008` based on main `5b74d686d44ff67f7473fe46d8fcb7a9904618bf`.

**Scope:** fix two ambiguous phrases in PROPOSED ADRs without authorizing a schema/code change, LIVE Google Flow action, or merge. Existing 30 UI references, 22 approved E12-02 UI screenshots and account/credit gates are unchanged.

## Clarification F01 — canonical safe failure

- Use exactly one planned safe-failure state name: **`FAILED_SAFE`**. The former `SAFE_FAILURE` phrase in ADR-022 was inconsistent.
- A transition from `SUBMIT_STARTED` to `FAILED_SAFE` requires **conclusive account-bound evidence** that a billable provider Generate was never accepted.
- Missing remote ID, a timeout, lost browser connection, app crash, or stale local progress alone are **not** such evidence.
- When acceptance cannot be proved or ruled out, state is `SUBMIT_UNCERTAIN`: keep the existing account's reservation **HELD**, pause mutation, allow read-only reconciliation only. No automatic retry, reassign, or spend migration.
- Existing legacy project job enum is unchanged; the coordinator state model remains proposed.

## Clarification F02 — READY after full restart

- Every newly started application process begins with the profile **not READY** until it verifies the existing Chrome session, correct account identity and per-profile worker ownership in that process.
- Stored evidence from earlier runs is **audit history only**, not present session authorization.
- Session READY **does not imply** owner opt-in, provider permission, verified entitlement or credit availability. Those gates are separate and deny-by-default.
- A stale worker/fencing token or another process owning the coordinator prevents mutable jobs even with a valid signed-in browser.

## Planned fake-only acceptance tests (required later; NONE EXECUTED HERE)

| ID | Fake scenario | Expected fail-closed result |
|---|---|---|
| F01-T1 | Timeout after `SUBMIT_STARTED` | `SUBMIT_UNCERTAIN`, credit HELD, no second Generate |
| F01-T2 | Conclusive driver proof no accepted mutation | `FAILED_SAFE` permitted, immutable evidence recorded |
| F01-T3 | Missing result ID but still generating remotely | Never infer `FAILED_SAFE`; read-only reconcile |
| F02-T1 | App fully restarted with last-run READY persisted | New process starts non-READY; no live dispatch |
| F02-T2 | Manual login succeeded but policy unknown | Profile may be session READY, **live mutation still BLOCKED** |
| F02-T3 | Worker from prior process attempts stale fenced mutation | Refused; state/credit evidence preserved |
| F02-T4 | Account session belongs to wrong profile ID | No READY for requested profile; cross-account result access denied |

## Remaining owner/implementation decisions

The edits are narrow errata to text, **not T06 owner approval**. ADR-020..023 remain **PROPOSED**, G0 strict BLOCKED, G1 policy UNKNOWN, G4 binary archive PENDING, G5 live tariff/saldo UNKNOWN, G6 restart READY UNVERIFIED and migration/fencing tests are not performed. The PR must remain **DRAFT/unmerged**. The review of T06 is complete only after the owner signs off D01–D06 and remaining gates are evidenced; still no coding until all gates PASS.

This document is a proposed acceptance-test contract, **not** a report of executed tests.
