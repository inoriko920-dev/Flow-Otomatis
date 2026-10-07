# Flow-Otomatis

Flow-Otomatis is a Windows 11 desktop application for deterministic scene-based Google Flow production orchestration.

## Software Factory status
- STEP 00–10: completed through the Minimum End-to-End Vertical Slice.
- STEP 10: **PASS**.
- Next: **STEP 11 — Feature Implementation Waves**.
- Real Google login, live Google Flow generation, live video download, and Gemini external integration are **NOT TESTED**; external services belong to STEP 12.

## What is real now
- Production PySide6 App Shell based on the frozen 30-state UI reference.
- Episode Package picker and FLOW_OTOMATIS_IMPORT.json validation.
- Safe ZIP/package parsing with traversal protection.
- Real scene timing/readiness derivation.
- Approved-image existence validation.
- Recomputed 4/6/8/10 Flow-duration recommendation from Target.
- Per-project SQLite workspace persistence.
- Frozen Validation/Workspace UI bound to real imported package state.
- Windows portable onedir build and smoke test.

## STEP 10 verification
- Tested implementation SHA: 64903913e83cbb9d86909b0c1c255585b2295351.
- CI run: 37590300417 — SUCCESS.
- Ruff + mypy + architecture guard: PASS.
- pytest: 32 passed.
- Frozen UI regression: 30/30 PASS.
- Visual similarity: 0.6344–0.9643, threshold 0.55.
- Windows artifact ID: 11468466375.
- Windows artifact SHA-256: 5372cc919f7194085705e920eddcacff2d6654eef5e5ff9a2cae9268ede1e83d.
- Portable EXE smoke: PASS.

## Frozen product rules
- Windows 11 x64, portable multi-file ZIP.
- Indonesian-first desktop UI.
- Biography production lock: Omni Flash 1.1 • 720p • 16:9.
- Audio/SRT Target Duration remains authoritative.
- Flow generation duration is 4/6/8/10; app recommends, user confirms valid choice.
- Approved reference image maps by canonical SCENE_###.
- Generate and Download are separate.
- No CAPTCHA/MFA bypass, credential export, hidden account rotation, or quota/rate-limit evasion.

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

STEP 11 must preserve the frozen UI and build local features in small evidence-backed waves. External-service integration belongs to STEP 12.
