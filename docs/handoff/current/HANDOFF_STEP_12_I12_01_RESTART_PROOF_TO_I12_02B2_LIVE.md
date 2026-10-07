# HANDOFF — STEP 12 / I12-01 RESTART-PROOF → I12-02B2-LIVE

## Gate
I12-01 automated lifecycle + restart-proof hardening: **PASS**.

I12-01 real-account validation: **PENDING**.

I12-02B2-LIVE — Live One-Scene Google Flow Submit Driver: **BLOCKED** until the product owner's real local Google profile proves READY across an actual application restart.

## Tested baseline
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- Tested implementation SHA: `6abfbc169a0864c00f1136cfc7dd6a7fe7583b8a`
- CI: `37617108389` — SUCCESS
- Quality: `112778002338` — SUCCESS
- UI visual: `112778281237` — SUCCESS
- Windows package: `112778575235` — SUCCESS
- pytest: **85 passed**
- mypy: **62 source files**
- UI regression: **30/30 PASS**

## Restart-proof contract
The Browser Worker now persists only credential-free evidence:
- first READY app-instance id;
- first READY timestamp;
- restart verified timestamp.

Rules:
- first READY alone is not enough;
- another READY in the same app process is not enough;
- READY from a later app instance establishes restart persistence;
- current state must still be READY;
- if state becomes NEEDS_LOGIN, the live gate is false even if restart had been verified previously.

The evidence file does not contain passwords, cookies, tokens, credentials, browser-data, or session contents.

## UI visibility
The real Bantuan Login surface now exposes the restart gate directly:
- `Restart belum diverifikasi` when the current session is READY but no cross-instance proof exists;
- `Restart berhasil diverifikasi` when READY was observed again after a real app restart;
- `Validasi restart: Belum lulus / Lulus` is shown in the safe-status card;
- the user is instructed to fully close, reopen, then run Cek Ulang Sesi again.

This allows the product owner to report the gate result without inspecting files or sharing session data.

## Artifacts
- UI evidence:
  - ID: `11480590257`
  - digest: `sha256:7b6c4ce3d7dd4ea8048bdd8ade8deb0a3c079cedbf57d057c867be65f775f0bf`
- Windows portable:
  - ID: `11480900497`
  - size: `435468948` bytes
  - digest: `sha256:cfbb320859360b877f3362684915cc32db1e11aa33ce39d8421f5a2e3b631b4a`

## Mandatory runtime gate contract
`RestartGatedGenerationProvider` is now tested and must wrap any future live Flow generation provider.

Behavior:
- restart gate not passed → `GenerationAuthenticationRequiredError`;
- current state not READY → blocked;
- blocked path → zero downstream provider calls;
- gate passed → exactly one downstream generation call;
- queue maps authentication-required to ATTENTION_REQUIRED.

Important: `bootstrap/main.py` does not yet compose a live Google Flow generation provider. This is deliberate. The guard is ready for live wiring but does not prove live Generate works.

Latest artifacts:
- UI evidence: `11480692141`, digest `sha256:b7ec06b0ec28fe330c8dae6467efd963ef353e538bccf5ca4ee6be740c725bc6`
- Windows portable: `11481001812`, size `435469955` bytes, digest `sha256:e24ff70fb31cc8ffa31de2fa1f6af5507f742d6ace49bf77d5ad548e1dd19d75`

## Still not proven
CI cannot prove:
- the product owner's Google account is authenticated;
- the user's real Google session survives restart;
- current live Flow generation controls/selectors;
- live upload/prompt/settings/Generate behavior.

No live Flow mutation was added in this slice.

## Required local validation
1. Run the latest Windows artifact.
2. Open/create one user-owned Google profile.
3. Complete Google login manually.
4. Use Cek Ulang Sesi until profile state is READY/Siap.
5. Fully close the application.
6. Reopen the application.
7. Check the same profile again and confirm the UI shows `Restart berhasil diverifikasi` and `Validasi restart: Lulus`.

Do not share password, MFA code, cookies, tokens, browser-data, or session files.

## Next exact action
Only after the real local validation succeeds and the product owner explicitly says `lanjutkan`:
- mark I12-01 real-account validation PASS;
- start I12-02B2-LIVE for exactly one Scene;
- wrap the live provider with `RestartGatedGenerationProvider`; direct ungated wiring is forbidden;
- inspect the current authorized Flow UI before selector locking;
- perform at most one mutating submit attempt;
- no silent retry;
- ambiguous outcome → ATTENTION_REQUIRED;
- do not combine download or Gemini with this slice.
