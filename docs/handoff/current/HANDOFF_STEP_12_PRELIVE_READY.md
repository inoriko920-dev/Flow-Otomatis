# HANDOFF — STEP 12 PRE-LIVE READY

## Status
PRE-LIVE READY.

All work that can be implemented and verified safely without the product owner's real authorized Google/Flow session is complete.

## Verified code baseline
- main implementation SHA: `8246d194a56cfdbf3c2818a570dc637a37633891`
- official CI: `37664172842` — SUCCESS
- quality: `112939012288` — 128 tests PASS, mypy 80 source files, architecture PASS
- frozen UI: `112939602875` — 30/30 PASS
- Windows package: `112940003453` — Chromium + portable smoke PASS
- Windows artifact: `11502048305`
- size: 435713508 bytes
- SHA-256: `631ab49ed5f7a3f7c99f9df496fd8109625efa25288bf5e7bc66c2865c6c69ed`

## Completed before live login
- full local import/planning/project/result persistence;
- audit remediation F01–F06;
- safe session/restart gate and non-blocking Browser Worker;
- one-submit anti-duplicate/ambiguity contracts;
- read-only Flow preflight and request validation;
- I12-03A safe Download foundation;
- I12-04A Gemini keyring + masked metadata + health check;
- I12-04B read-only Gemini AI Agent.

## Manual product-owner gate
Using the Windows artifact:
1. open Flow-Otomatis;
2. Profil Google → create/open a profile;
3. Buka/Fokuskan Sesi Login;
4. finish Google login manually in installed normal Chrome;
5. close the login Chrome window;
6. Cek Ulang Sesi until the profile is READY;
7. fully close Flow-Otomatis;
8. reopen it;
9. check the same profile and confirm `Validasi restart: Lulus`.

Never share password, MFA code, cookie, token, or browser-data.

## After the gate passes
Continue I12-02B2-LIVE:
- inspect the current authorized Flow UI;
- lock only verified selectors;
- use the existing RestartGatedGenerationProvider;
- exactly one Scene and one mutating submit attempt;
- no silent retry;
- ambiguous outcome -> ATTENTION_REQUIRED.

Only after a stable live remote result identity exists, continue I12-03-LIVE:
- detect the live result;
- implement the current verified download selector/flow;
- reuse I12-03A atomic .part -> final file semantics;
- Generate and Download remain separate.

## Gemini
Gemini Keys and read-only AI Agent are already wired. A user-owned key can be imported and health-checked independently of Flow login. Key/model rotation remains manual; no quota-evasion automation exists.
