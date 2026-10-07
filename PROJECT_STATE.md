# PROJECT_STATE — Flow-Otomatis

## Current verified baseline
- Repository: inoriko920-dev/Flow-Otomatis
- Branch: main
- Factory STEP completed: STEP 09 — App Shell/UI Implementation
- STEP 09 status: PASS
- Last tested implementation SHA: ee90740ba6e620af1107d73b19b6753395aa26bd
- Final STEP 09 CI run: 37587748975 — SUCCESS
- UI visual evidence artifact ID: 11467640780
- Windows portable artifact ID: 11467562919
- Windows artifact outer ZIP size: 387245835 bytes
- Windows artifact outer ZIP SHA-256: 4ec31ef23ddeda873177f6f359704543624c19005b83e45fd6834eb398653f90
- Inner portable ZIP size: 387667735 bytes
- Inner portable ZIP SHA-256: 14006921da4d119c0de2d713e32ab8a2a58d0e534ccdb3f5f025914253e166d6
- Downloaded artifact checksum verification: PASS
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
- STEP 09: PASS
- NEXT: STEP 10 — SLC-001 Import / Validate Episode Package → Create Real Workspace State

## STEP 09 evidence

### S09-T01 — Production App Shell + Frozen UI States
PASS.
- Production PySide6 App Shell implemented.
- Canonical 7-item navigation implemented.
- Top project/status bar, main content host, optional Scene/AI Agent right dock, and bottom status bar implemented.
- Frozen UI fixture registry contains 30/30 STEP 04 states.
- UI production settings preserve Omni Flash 1.1 • 720p • 16:9.
- Scene Target timing remains authoritative.
- Flow duration remains restricted to 4/6/8/10.
- Dialog overlays render over their real background screens.
- No presentation-layer direct ownership of SQLite, filesystem, Playwright, keyring, or provider SDK.

### S09-T02 — Semantic / Interaction UI Verification
PASS.
- Ruff format PASS.
- Ruff lint PASS.
- mypy strict PASS.
- architecture guard PASS.
- unit/contract/smoke/UI semantic tests PASS.
- Navigation mouse click PASS.
- Keyboard navigation focus PASS.
- Escape closes frozen modal states PASS.
- Minimum 1366×768 resize smoke PASS.
- Canonical screenshot viewport: 1920×1080.

### S09-T03 — ACTUAL vs Frozen REFERENCE
PASS.
- 30/30 ACTUAL screenshots captured from production code.
- 30/30 visual fixtures PASS.
- Similarity threshold: 0.550.
- Similarity range: 0.6344–0.9643.
- Visual evidence artifact ID: 11467640780.
- Visual artifact ZIP SHA-256: dc68142e82638c7bbe200c4efbf7009307bfcb330a55fc7e79d32be1337822c5.
- No frozen screen remains FAIL/BLOCKED.

### S09-T04 — Windows Portable UI Build
PASS.
- Playwright Chromium staging PASS.
- Bundled Chromium smoke PASS.
- PyInstaller onedir build PASS.
- Portable EXE launch/exit smoke from foreign CWD PASS.
- Portable artifact uploaded and downloaded successfully.
- Outer artifact ZIP integrity PASS.
- Inner portable ZIP checksum matched SHA256SUMS exactly.
- Windows artifact ID: 11467562919.

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
- Frozen STEP 09 App Shell must not be silently redesigned during STEP 10.

## Known limitations after STEP 09
- Current screen data is still deterministic fixture data where real application services are not yet connected.
- Live Google login, live Flow generation, and live Flow download are NOT TESTED.
- Sidebar symbol glyphs remain deterministic placeholders and are not a STEP 10 redesign target.
- Provider/persistence wiring is intentionally deferred to later vertical slices.

## Next exact action
STEP 10 must implement only **SLC-001 — Import / Validate Episode Package → Create Real Workspace State**.

Required STEP 10 proof:
1. select a biography episode package;
2. validate FLOW_OTOMATIS_IMPORT.json;
3. verify Scene IDs, approved-image mapping, motion prompt presence, Target timing, and valid Flow-duration rules;
4. derive real Scene readiness in domain/application code;
5. persist a minimal real project/workspace state;
6. render existing frozen Import/Validation/Workspace UI from the real state;
7. prove one happy path and one representative failure path with integration/contract tests.

Do not start live Google Flow generation/login/download in STEP 10.
