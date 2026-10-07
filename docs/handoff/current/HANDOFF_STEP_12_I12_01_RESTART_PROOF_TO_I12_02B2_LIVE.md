# HANDOFF — STEP 12 / I12-01 RESTART-PROOF → I12-02B2-LIVE

## Gate
I12-01 automated lifecycle + restart-proof hardening: **PASS**.

I12-01 real-account validation: **PENDING**.

I12-02B2-LIVE — Live One-Scene Google Flow Submit Driver: **BLOCKED** until the product owner's real local Google profile proves READY across an actual application restart.

## Tested baseline
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- Tested implementation SHA: `cbfaa368fd051e0d0a648643bba0fa76484b7d8d`
- CI: `37633516723` — SUCCESS
- Quality: `112833623396` — SUCCESS
- UI visual: `112834024070` — SUCCESS
- Windows package: `112834514993` — SUCCESS
- pytest: **90 passed**
- mypy: **63 source files**
- UI regression: **30/30 PASS**

## System Chrome authentication fix
The old Playwright-controlled login surface was replaced after the product owner reproduced Google's "browser or app may not be secure" rejection.

Required lifecycle:
1. manual sign-in opens installed Google Chrome in normal mode using the isolated app profile;
2. no Playwright, CDP, remote-debugging, stealth, or bypass flags are active during authentication;
3. the product owner completes login/MFA/CAPTCHA manually;
4. the normal login Chrome window is fully closed;
5. only then does Cek Ulang Sesi relaunch the same profile with a random localhost CDP endpoint and attach Playwright;
6. authorization is probed without exporting credentials/session contents.

Latest artifacts:
- UI evidence: `11487353178`, digest `sha256:cae786100222df13c8da3dfd0c36ba86390b40ff211ee8b6473b9596f974328d`
- Windows portable: `11486833906`, size `435478667` bytes, digest `sha256:d99e356615899f2eb9d5f99a3d1b8f37e315e3857cd14990acd432acc3c6baca`

CI proves implementation/build safety only. Real Google account acceptance is still PENDING product-owner Windows validation.

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
3. Choose Buka / Fokuskan Sesi Login.
4. Complete Google login manually in the normal installed Google Chrome window.
5. After login succeeds, fully close that Chrome login window.
6. Return to Flow-Otomatis and choose Cek Ulang Sesi; confirm READY/Siap.
7. Fully close Flow-Otomatis.
8. Reopen Flow-Otomatis.
9. Check the same profile again and confirm `Restart berhasil diverifikasi` and `Validasi restart: Lulus`.

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
