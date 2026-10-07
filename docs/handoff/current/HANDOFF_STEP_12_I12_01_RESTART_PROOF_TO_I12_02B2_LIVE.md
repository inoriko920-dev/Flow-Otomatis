# HANDOFF — STEP 12 / I12-01 RESTART-PROOF → I12-02B2-LIVE

## Gate
I12-01 automated lifecycle + restart-proof hardening: **PASS**.

I12-01 real-account validation: **PENDING**.

I12-02B2-LIVE — Live One-Scene Google Flow Submit Driver: **BLOCKED** until the product owner's real local Google profile proves READY across an actual application restart.

## Tested baseline
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- Tested implementation SHA: `0e6b8e3755721954a0d2be8d712f0af88e961e4a`
- CI: `37615288655` — SUCCESS
- Quality: `112772031746` — SUCCESS
- UI visual: `112772307027` — SUCCESS
- Windows package: `112772535490` — SUCCESS
- pytest: **79 passed**
- mypy: **61 source files**
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

## Artifacts
- UI evidence:
  - ID: `11479174307`
  - digest: `sha256:5c92598d30204c77723c07ad66faa1673f24d27092eceb040c56768123709245`
- Windows portable:
  - ID: `11479739543`
  - size: `435467636` bytes
  - digest: `sha256:736b3a7b95ece7dd64a0516f0b147934050bf8ba61b6ae2957e9eef073f56107`

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
7. Check the same profile again and confirm it is still READY/Siap.

Do not share password, MFA code, cookies, tokens, browser-data, or session files.

## Next exact action
Only after the real local validation succeeds and the product owner explicitly says `lanjutkan`:
- mark I12-01 real-account validation PASS;
- start I12-02B2-LIVE for exactly one Scene;
- inspect the current authorized Flow UI before selector locking;
- perform at most one mutating submit attempt;
- no silent retry;
- ambiguous outcome → ATTENTION_REQUIRED;
- do not combine download or Gemini with this slice.
