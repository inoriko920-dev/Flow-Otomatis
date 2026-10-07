# TASKS — Flow-Otomatis

## STEP 08 — Repository Foundation
Status: PASS.

### S08-T01 — Documentation Source-of-Truth Bootstrap
- Status: PASS.
- Evidence: source-of-truth binary commit af1ac445abcaee4eadc5be1f0875761d789368f9.
- 13/13 mandatory binary DOCX paths verified by Git blob SHA.

### S08-T02 — Repository Skeleton + Quality Tooling
- Status: PASS.
- Foundation implementation/tooling verified on Windows Python 3.14.7.
- Successful workflow: 37583227824.
- uv.lock commit: 9c496506dbc35ddfca0f793c847e35e4b7ccb0cc.

### S08-T03 — Windows CI + Portable Foundation Smoke
- Status: PASS.
- Last tested implementation SHA: 539ffb8e25a2f52492a6fbf3de4df805ca670742.
- Successful CI run: 37583870436.
- Artifact: Flow-Otomatis-foundation-win-x64, ID 11465692132.
- Live Google Flow: NOT TESTED.

## STEP 09 — App Shell/UI Implementation
Status: PASS.

### S09-T01 — Production App Shell + 30 Frozen States
- Status: PASS.
- Production shell and shared presentation components implemented.
- 30/30 frozen STEP 04 UI states implemented.
- Frozen production profile remains Omni Flash 1.1 • 720p • 16:9.
- Presentation architecture boundary preserved.

### S09-T02 — Semantic / Interaction UI Verification
- Status: PASS.
- Ruff format/lint: PASS.
- mypy strict: PASS.
- architecture guard: PASS.
- unit/contract/smoke/UI semantic tests: PASS.
- Mouse navigation, keyboard focus, Escape modal close, and 1366×768 resize smoke: PASS.

### S09-T03 — ACTUAL vs REFERENCE Visual Gate
- Status: PASS.
- 30/30 ACTUAL screenshots captured at 1920×1080.
- 30/30 comparison PASS.
- Threshold: 0.550.
- Similarity range: 0.6344–0.9643.
- Evidence artifact ID: 11467640780.
- Evidence artifact digest: dc68142e82638c7bbe200c4efbf7009307bfcb330a55fc7e79d32be1337822c5.

### S09-T04 — Windows Portable UI Build
- Status: PASS.
- Last tested implementation SHA: ee90740ba6e620af1107d73b19b6753395aa26bd.
- Successful CI run: 37587748975.
- Artifact: Flow-Otomatis-step09-ui-win-x64, ID 11467562919.
- Outer artifact size: 387245835 bytes.
- Outer artifact SHA-256: 4ec31ef23ddeda873177f6f359704543624c19005b83e45fd6834eb398653f90.
- Inner portable ZIP size: 387667735 bytes.
- Inner portable ZIP SHA-256: 14006921da4d119c0de2d713e32ab8a2a58d0e534ccdb3f5f025914253e166d6.
- Downloaded artifact checksum verification: PASS.
- Portable EXE smoke: PASS.
- Live Google Flow: NOT TESTED.

## NEXT — STEP 10
**SLC-001 — Import / Validate Episode Package → Create Real Workspace State**

Scope:
- real package selection/import;
- FLOW_OTOMATIS_IMPORT.json validation;
- real Scene/image/prompt/Target/duration readiness;
- minimal persisted project/workspace state;
- frozen Import/Validation/Workspace UI connected to real state;
- one happy-path integration proof;
- one representative failure-path proof.

Out of scope for STEP 10:
- live Google login;
- live Google Flow generation;
- live video download;
- silent redesign of the frozen STEP 09 UI.

Do not implement STEP 10 until the product owner says "lanjutkan".
