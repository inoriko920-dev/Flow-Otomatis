# Flow-Otomatis

Flow-Otomatis is a Windows 11 desktop application project for deterministic scene-based Google Flow production orchestration.

## Current factory status
- STEP 00–07 planning: complete.
- STEP 08 Repository Foundation: **IN PROGRESS / DOCUMENTATION GATE**.
- Production source code: **NOT ALLOWED YET**.
- First implementation gate: all planning DOCX, Final UI Reference, UI PNG references, and handoff files must exist in this repository before `src/` production code is created.

## Frozen product rules
- Windows 11 x64, portable multi-file ZIP.
- Indonesian-first desktop UI.
- Architecture target: CPython 3.14.x + PySide6 Qt Widgets + Playwright Chromium Browser Worker.
- Biography workflow production lock: Omni Flash 1.1 • 720p • 16:9.
- Audio/SRT Target Duration remains authoritative.
- Flow generation duration is one of 4/6/8/10 seconds; app recommends, user confirms a valid value.
- Approved reference image is auto-mapped by canonical `SCENE_###`.
- Generate and Download are separate states.
- No CAPTCHA/MFA bypass, credential export, hidden account rotation, or quota/rate-limit evasion.

## Source of truth
Read `AGENTS.md`, `PROJECT_STATE.md`, `TASKS.md`, and the files under `docs/` before any implementation work.

> Repository bootstrap note: the connected GitHub write interface used for this bootstrap supports UTF-8 text writes but not direct binary DOCX/PNG upload. Therefore STEP 08 remains blocked for coding until the binary source-of-truth files listed in `docs/planning/SOURCE_OF_TRUTH_MANIFEST.md` are physically present in the repository and verified by hash.
