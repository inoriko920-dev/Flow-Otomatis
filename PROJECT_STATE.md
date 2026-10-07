# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Repository was greenfield/empty before STEP 08.
- Initial documentation guard commit: 164ef0073115d1e0178a1c6eb920443e761cd35e
- Current Factory STEP: STEP 08 — Repository Foundation
- Current task: S08-T01 Documentation Source-of-Truth Bootstrap
- Production source code status: FORBIDDEN / NOT STARTED

## STEP status
- STEP 00: PASS
- STEP 01: PASS
- STEP 02: PASS
- STEP 03: PASS
- STEP 04: PASS
- STEP 05: PASS_WITH_PROVISIONAL
- STEP 06: PASS_WITH_PROVISIONAL
- STEP 07: PASS_WITH_PROVISIONAL
- STEP 08: IN PROGRESS / BLOCKED ON BINARY SOURCE-OF-TRUTH

## Why coding is blocked
The connected GitHub write interface in this session can create UTF-8 text files, but does not expose direct binary DOCX/PNG upload. User rules require all planning DOCX and final UI references to be physically present in the repository before coding. Therefore source code must NOT be created until the binary files in docs/planning/SOURCE_OF_TRUTH_MANIFEST.md and docs/ui/UI_REFERENCE_MANIFEST.md are present and hash-verified.

## Frozen decisions
- CPython 3.14.x x64 + PySide6 Qt Widgets.
- Playwright Chromium in dedicated Browser Worker process.
- Modular monolith + ports/adapters.
- SQLite global DB + per-project DB.
- Windows Credential Locker/keyring for API secrets.
- PyInstaller onedir portable ZIP.
- Serial R1 generation queue.
- Omni Flash 1.1 • 720p • 16:9 for biography workflow.
- Audio/SRT Target remains authoritative.
- Flow duration 4/6/8/10: app recommends, user confirms valid value.
- Approved image auto-mapped by SCENE_###.
- Generate and Download are separate.
- No CAPTCHA/MFA bypass, no credential export, no quota/rate-limit evasion.

## Blocker
B08-DOCBIN-001 — Mandatory DOCX/PNG source-of-truth binaries are not yet uploaded through the available connector.

## Next exact action
Upload the binary DOCX/PNG source-of-truth files listed in the manifests, verify hashes, then mark S08-T01 PASS. Only after that may S08-T02 create src/ and dependency tooling.
