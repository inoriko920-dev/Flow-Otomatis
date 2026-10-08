# Flow-Otomatis

## Verified update — 8 October 2026
- STEP 12 ASTRA bug audit B01–B06: **OFFLINE PASS** (R00–R04).
- Independent release integrity hardening: **PASS**, PR #18 merged `baff19bb7c28612837d24001b9db9ee4a84251e5`.
- Full official `main` CI `37728080637`: **217 pytest passed**, **30/30** frozen UI, Chromium/portable EXE smoke plus packaged ZIP SHA-256/CRC/source/path verification PASS.
- Portable ZIP now includes `THIRD_PARTY_NOTICES.txt` after correcting its build order; verifier checks 1,049 packaged files.
- Manual Google login reported working by product owner; **READY after full app restart remains unverified**. Live Generate/Download is not implemented/accepted as ready.
- Latest evidence: `docs/planning/audits/STEP12_PORTABLE_RELEASE_INTEGRITY_EVIDENCE_2026-10-08.md`.
- Last CI artifact is temporary (expires 22 October 2026 UTC); not an off-platform backup.


Flow-Otomatis is a Windows 11 desktop application for deterministic scene-based Google Flow production orchestration.

## Software Factory status
- STEP 00–11 completed through local Feature Implementation Waves.
- STEP 11: **PASS**.
- Next: **STEP 12 — Integrations & External Services**.
- Real Google login, live Google Flow generation/download, and Gemini external integration are still **NOT TESTED**.

## What is real now
- Production PySide6 App Shell based on the frozen 30-state UI reference.
- Episode Package picker and FLOW_OTOMATIS_IMPORT.json validation.
- Safe ZIP/package parsing with traversal protection.
- Real Scene timing/readiness derivation.
- Persisted Flow-duration selection with Target validation.
- Approved-image rescan/readiness refresh.
- Per-project SQLite workspace persistence.
- Real local Project Hub and persisted-project reopen.
- Durable serial R1 generation queue with provider-neutral boundary.
- Local queue behavior proven with a fake provider.
- Generate and Download stored as separate states.
- Real local Hasil screen.
- Atomic credential-free FLOW_OTOMATIS_RESULT.json handoff export.
- Windows portable onedir build and smoke test.

## STEP 11 verification
- Tested implementation SHA: 75a896ccf3754a225414c34de9f88d5d9a8b5581.
- CI run: 37597279499 — SUCCESS.
- Ruff + mypy + architecture guard: PASS.
- pytest: 43 passed.
- Frozen UI regression: 30/30 PASS.
- Visual similarity: 0.6344–0.9643, threshold 0.55.
- UI evidence artifact ID: 11471336385.
- Windows artifact ID: 11471780918.
- Windows artifact digest: b85a3541f03524d65c439912dd4c7afd98ab1727c7661b5cf5487e73895b481d.
- Portable application smoke: PASS.

## Frozen product rules
- Windows 11 x64, portable multi-file ZIP.
- Indonesian-first desktop UI.
- Biography production lock: Omni Flash 1.1 • 720p • 16:9.
- Audio/SRT Target Duration remains authoritative.
- Flow generation duration is 4/6/8/10; app recommends, user confirms a valid choice.
- Approved reference image maps by canonical SCENE_###.
- Generate and Download are separate.
- No CAPTCHA/MFA bypass, credential export, hidden account rotation, or quota/rate-limit evasion.

## External-service boundary
STEP 12 will introduce external services incrementally:
1. authorized Google session/manual login lifecycle;
2. one-Scene deterministic Google Flow generation adapter;
3. live result detection/download;
4. Gemini AI Agent/key integration.

No live-provider readiness is claimed from STEP 11 evidence.

## Source of truth
Before modifying implementation, read:
1. AGENTS.md
2. PROJECT_STATE.md
3. TASKS.md
4. docs/software_factory/
5. docs/planning/
6. docs/ui/
7. docs/architecture/
8. docs/adr/
9. docs/handoff/current/

STEP 12 must preserve the frozen UI and existing local domain/persistence boundaries. External integrations must include timeout, cancel, idempotency/retry rules, credential redaction, fixture mode, and explicit error mapping.
