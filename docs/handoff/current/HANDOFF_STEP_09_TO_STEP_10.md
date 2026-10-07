# HANDOFF STEP 09 → STEP 10

## Project / baseline
- Project: Flow-Otomatis
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- Last tested implementation SHA: `ee90740ba6e620af1107d73b19b6753395aa26bd`
- CI run: `37587748975` — SUCCESS
- UI Blueprint / Freeze: `PB-FLOW-OTOMATIS-v1.0 / UIF-FLOW-OTOMATIS-v1.0`

## Foundation status
- STEP 08 Repository Foundation: PASS.
- STEP 09 App Shell/UI Implementation: PASS.
- CPython 3.14.7 + PySide6 6.11.2 + Playwright 1.63.0 + PyInstaller onedir verified on Windows CI.

## App Shell status
Production App Shell exists and runs:
- canonical 7-item sidebar;
- top project/status bar;
- flexible main content;
- optional Scene / AI Agent right dock;
- bottom status bar;
- modal overlay behavior;
- deterministic fixture route used by both app and screenshot evidence.

## Screen coverage
- Frozen UI states implemented: **30/30**.
- Visual parity gate: **30/30 PASS**.
- Similarity range: **0.6344–0.9643**, threshold 0.55.
- Semantic UI contract tests: PASS.
- FAIL/BLOCKED screens: NONE.
- PASS_WITH_TOLERANCE screens: NONE as gate status; normal renderer variance is documented as non-semantic tolerance.

## Component registry
Canonical presentation owners:
- `presentation/main_window.py`
- `presentation/theme.py`
- `presentation/widgets.py`
- `presentation/fixtures.py`
- `presentation/screen_factory.py`
Presentation must remain free from direct SQLite, filesystem, Playwright, keyring, and provider SDK ownership.

## State coverage
Deterministic state set covers first-run, recovery, ready workspace, serial running batch, session attention, image mapping errors, successful/partial result, handoff, login, key vault, diagnostics, ambiguous external job, AI preview/approval, duration selection, package validation, destructive confirmation, running-batch close, and paid-provider consent.

## Viewport / input evidence
- Canonical capture: 1920×1080.
- Minimum resize smoke: 1366×768 PASS.
- Navigation mouse click: PASS.
- Keyboard focus on navigation: PASS.
- Escape modal close: PASS.
- Packaged GUI launch/exit smoke: PASS.

## CI / artifact evidence
- Run: `37587748975`
- UI evidence artifact ID: `11467640780`
- Windows package artifact ID: `11467562919`
- Windows artifact uploaded size: 387245835 bytes.
- Windows artifact ZIP digest reported by Actions: `4ec31ef23ddeda873177f6f359704543624c19005b83e45fd6834eb398653f90`.
- Live Google Flow: **NOT TESTED**.

## Known UI debt
- Sidebar symbol glyphs are deterministic placeholders for iconography; do not replace them through a silent redesign.
- Provider/persistence values are fixture data only until real application services are connected.
- No open UI Change Request.

## Recommended STEP 10 vertical slice
**SLC-001 — Import / Validate Episode Package → Create Real Workspace State**

### Why this slice
It proves the architecture end to end without introducing live Google/provider uncertainty:
1. user selects a biography episode package;
2. application validates `FLOW_OTOMATIS_IMPORT.json`;
3. safe package/filesystem adapter verifies Scene IDs, approved image mapping, prompt presence, Target timing and duration rules;
4. domain produces real Scene readiness;
5. persistence stores a minimal real project/workspace state;
6. Workspace UI reads the real state instead of fixture rows.

### Happy path
A valid small synthetic package imports and produces a persisted workspace with real scene rows and correct readiness/duration recommendation.

### Representative failure path
Package is rejected safely for one representative contract error such as:
- missing approved image;
- duplicate image mapping;
- malformed/unsupported manifest;
- Target >10s.

No Google account or live generation is needed for STEP 10.

## Exact next task
Start STEP 10 only after product-owner command **“lanjutkan”**:
1. read this handoff + STEP 06 architecture + STEP 07 Code Constitution;
2. define the smallest SLC-001 command/domain/contracts/repository seams;
3. implement one happy path and one representative failure path;
4. connect the existing frozen Import/Validation/Workspace UI without redesign;
5. add integration/contract tests and CI evidence;
6. stop after the one vertical slice is proven.

## Rollback / recovery
STEP 10 should be additive behind application ports. If the slice fails, revert/correct slice commits without changing the frozen STEP 09 App Shell or reference UI.
