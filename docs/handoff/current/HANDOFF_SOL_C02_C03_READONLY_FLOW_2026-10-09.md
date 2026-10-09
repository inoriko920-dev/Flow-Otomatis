# SOL C02–C03 — Read-Only Flow Preflight, Single Actor & Qt UI (9 October 2026)

Branch: `sol/c01-google-session-runtime-freshness-20261009`, Draft PR #32. **No merge or release approval**. Baseline main `5b74d686d44ff67f7473fe46d8fcb7a9904618bf`; PR #31 remains separately Draft.

## Implementation
- Reuse `GoogleFlowPreflightWorker`, `SystemChromeCdpPool`, `ThreadedGoogleSessionCommands` and `GoogleSessionService`. Bootstrap constructs ONE shared pool and ONE single-thread command executor for session and read-only Flow checks.
- `submit_check_flow(profile_id)` checks this process's effective Google session status again inside the actor before touching Flow. Duplicate per-profile operations are refused by the existing worker lock. Qt does not access Playwright handles or call synchronous preflight.
- The pure Flow navigation classifier distinguishes Google login, generic official page reachability, onboarding, 401/403, and unknown/timeout/error. A public `labs.google` host only means `REACHABLE_ONLY` (legacy `REACHABLE` enum alias), **never ACCESS_VERIFIED**. No selectors or account identities are invented.
- The real manual-login Qt view has a single optional `Cek Akses Flow` action with independent Flow status and non-blocking result. Static 30 UI fixtures, navigation and scene/credit generation actions are not touched.
- Browser results are bound to the **requested profile_id** and UI operation epoch. Cross-profile replies, replies after invalidation, and replies after window close cannot restore cached status.
- Google session UNKNOWN from a prior run explicitly prompts `Perlu verifikasi ulang` rather than claiming user needs to log in again.

## Test/evidence boundaries
- Offline suite tests classifier, 401/403/login/onboarding, same-thread owner, READY guard, UI button, mismatched profile reply and stale epoch.
- Do not confuse Windows CI with authenticated browser testing. Positive Flow account identity/workspace proof has **not** been established and `ACCESS_VERIFIED` is intentionally never emitted by the classifier.
- C03 new optional button is within the existing REAL_GOOGLE_LOGIN dynamic action row; frozen fixture routes remain unchanged. UI approval for this additional dynamic action must be reviewed against G0/G4 references before merge.
- Live launch, manual login, identity proof, two complete app restarts, session-expired recovery and installed-Chrome/CDP are C04 operator actions. No credit or provider mutation permitted by this change.
- G0 archive/doc integration, G1 provider authorization, G5 credits/model and G6 live post-restart remain independent BLOCKED gates. Generate/download driver and multiaccount are out of scope.

## Acceptance tracking (offline vs live)
| ID | Evidence target | Status |
|---|---|---|
| AC01 | A/B/C third process no probe, downstream zero | Implemented fake regression; validate CI |
| AC02 | Failed recheck, login, cancel, shutdown revoke | Implemented fake regression; validate CI |
| AC03 | Google READY alone does not mean Flow connected | UI distinguishes session/Flow |
| AC04 | Public labs.google => reachability only | Pure classifier fixture |
| AC05 | Login/401/403/onboarding/unknown are distinct | Pure classifier fixture |
| AC06 | Different returned profile ID blocked | UI fake regression |
| AC07 | Stale callbacks denied | UI epoch fake regression |
| AC08 | Flow shares session actor | Worker integration regression |
| AC09 | Portable app, two real restarts | NOT RUN — real Windows operator required |
| AC10 | No real Generate/Download/credit/secret exposure | Offline-only code scope; LIVE NOT RUN |

No status in this file substitutes for an official PASS run at the exact final commit SHA.
