# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Factory STEP completed: STEP 08 — Repository Foundation
- STEP 08 status: PASS
- Last tested implementation SHA: 539ffb8e25a2f52492a6fbf3de4df805ca670742
- Final STEP 08 CI run: 37583870436 — SUCCESS
- Portable foundation artifact ID: 11465692132
- Portable inner ZIP size: 387634259 bytes
- Portable SHA-256: c8c000c59fe0beb4d4df961d7b348096fa3b15402b87ab5a43c20b79c22c1e1b
- Live Google Flow: NOT TESTED

## STEP status
- STEP 00: PASS
- STEP 01: PASS
- STEP 02: PASS
- STEP 03: PASS
- STEP 04: PASS
- STEP 05: PASS_WITH_PROVISIONAL
- STEP 06: PASS_WITH_PROVISIONAL
- STEP 07: PASS_WITH_PROVISIONAL
- STEP 08: PASS
- NEXT: STEP 09 — App Shell/UI Implementation + screenshot actual vs frozen reference

## STEP 08 evidence
### S08-T01 — Documentation Source-of-Truth Bootstrap
PASS.
- Complete Software Factory V2 TXT guide committed.
- STEP 00–07 planning/reference DOCX committed as binary Git blobs.
- STEP 04 active prompt DOCX committed.
- STEP 04 Final UI Reference DOCX contains all 30 approved UI compositions.
- Superseded STEP 04 planning versions archived.
- Binary blob verification: 13/13 matched expected Git blob SHA.

### S08-T02 — Repository Skeleton + Quality Tooling
PASS.
- CPython 3.14.7 verified on windows-2025 runner.
- uv 0.12.23 resolved 43 packages and committed uv.lock.
- PySide6 6.11.2, Playwright 1.63.0, Pydantic 2.13.5, keyring 25.7.0 installed.
- Ruff format/lint, mypy, architecture guard, unit/contract tests PASS.
- uv.lock commit: 9c496506dbc35ddfca0f793c847e35e4b7ccb0cc.
- Successful Foundation Lock run: 37583227824.

### S08-T03 — Windows CI + Portable Foundation Smoke
PASS.
- CI quality job PASS.
- Playwright Chromium staged and launched successfully against deterministic local content.
- PyInstaller onedir build PASS.
- Portable EXE smoke from foreign CWD containing spaces/Unicode PASS.
- Portable artifact uploaded and downloadable.
- Downloaded artifact outer ZIP integrity PASS.
- Portable ZIP checksum matched SHA256SUMS exactly.
- Final CI run: 37583870436.

## Frozen architecture/product decisions
- CPython 3.14.x x64 + PySide6 Qt Widgets.
- Playwright Chromium in dedicated Browser Worker process.
- Modular monolith + ports/adapters.
- SQLite global DB + per-project DB.
- Windows Credential Locker/keyring for API secrets.
- PyInstaller onedir portable ZIP.
- Serial R1 generation queue.
- Omni Flash 1.1 • 720p • 16:9.
- Audio/SRT Target remains authoritative.
- Flow duration 4/6/8/10: app recommends, user confirms valid selection.
- Approved image auto-mapped by SCENE_###.
- Generate and Download are separate.
- No CAPTCHA/MFA bypass, credential export, or quota/rate-limit evasion.

## Next exact action
STEP 09 must implement the production App Shell/UI from the frozen repository reference pack, then produce ACTUAL screenshots and compare them with the frozen REFERENCE. No silent redesign.
