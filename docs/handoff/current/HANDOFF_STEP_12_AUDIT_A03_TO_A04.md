# HANDOFF — STEP 12 AUDIT A03 → A04

## Gate
A03: **PASS**.

Verified baseline:
- main implementation: `3ee8d8118c1a137ac5c24d6ed7896b15bb3ccafb`
- CI: `37651619177` — SUCCESS
- quality: `112896105913`
- UI: `112896465371`
- Windows: `112896815896`
- pytest: 106 passed
- UI: 30/30 PASS
- portable smoke: PASS

Evidence:
- `docs/planning/audits/A03_REQUEST_REVISION_LEASE_RECOVERY_EVIDENCE_2026-10-07.md`

## Findings
Closed: F01, F02, F03, F04, F06.
Open: F05 only.

## A04 only
Follow ADR-017.

Required behavior:
- one dedicated Browser Worker execution owner controls browser/CDP runtime objects;
- Qt communicates through commands and sanitized status/result objects only;
- slow/failing browser operations must not block the Qt heartbeat;
- same-profile duplicate checks while busy are deterministic;
- startup, connect, probe/navigation, and shutdown use bounded timeout policies;
- cancellation and shutdown report their actual state honestly;
- preserve the current manual-authentication lifecycle and restart-proof behavior;
- keep the frozen UI unchanged.

Primary areas to inspect:
- Browser Worker runtime/bridge;
- Google session adapter/service;
- bootstrap composition;
- MainWindow session callbacks;
- close/shutdown lifecycle.

Acceptance:
- slow/failing driver test proves Qt remains responsive;
- duplicate-command behavior is covered;
- returned status objects contain no browser runtime objects;
- shutdown is bounded;
- existing session/restart tests remain PASS;
- 30-state UI visual regression PASS;
- Windows Chromium/portable smoke PASS.

Do not implement A05 in the same package. Existing live-operation gates remain unchanged.
