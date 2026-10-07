# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Initial repository state before STEP 08: greenfield/empty.
- Initial documentation guard commit: 164ef0073115d1e0178a1c6eb920443e761cd35e
- Latest verified HEAD after textual source-of-truth bootstrap: 2cfe510179d89582fc7ec8f9280f08e2649566e4
- Root tree verified: governance files + docs/ are present; src/ is absent.
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
- STEP 08: BLOCKED — S08-T01 binary source-of-truth incomplete

## Verified work completed in S08-T01
- README.md documentation guard.
- AGENTS.md AI working protocol.
- PROJECT_STATE.md / PLAN.md / TASKS.md.
- .gitignore / .gitattributes / .editorconfig.
- docs/architecture/ architecture, code constitution, module ownership, dependency rules, AI change protocol, ADR register.
- docs/handoff/current/ STEP07→08 handoff and explicit binary-upload blocker.
- docs/planning/SOURCE_OF_TRUTH_MANIFEST.md with canonical binary paths, sizes and SHA-256.
- docs/ui/UI_REFERENCE_MANIFEST.md with 30 final UI PNG hashes.
- docs/ui/IMPLEMENTATION_OVERRIDES.md.
- GitHub root verification confirms no src/ production source exists.

## Why coding is still blocked
The connected GitHub writer available in this session supports UTF-8 text creation/update but does not expose direct binary DOCX/PNG upload. The product-owner rule requires all planning DOCX and Final UI Reference assets to be physically present in the repo before coding.

Required binaries are enumerated in:
- docs/planning/SOURCE_OF_TRUTH_MANIFEST.md
- docs/ui/UI_REFERENCE_MANIFEST.md

Until every PENDING binary is present and hash-verified, S08-T01 is not PASS and S08-T02 must not start.

## Frozen technical/product decisions
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
- No CAPTCHA/MFA bypass, credential export, or quota/rate-limit evasion.

## Active blocker
B08-DOCBIN-001 — Mandatory DOCX/PNG source-of-truth binaries are not yet uploaded through the available GitHub connector.

## Work/evidence status
- Text governance/source-of-truth: VERIFIED IN GITHUB.
- Binary source-of-truth: NOT PRESENT / NOT VERIFIED.
- Production code: NOT STARTED.
- CI/build/package: NOT STARTED.
- Live Google Flow: NOT TESTED.

## Next exact action
Upload the binary DOCX/PNG source-of-truth files listed in the manifests, verify their hashes, then set S08-T01 PASS. Only after that may S08-T02 create src/ and dependency tooling.
