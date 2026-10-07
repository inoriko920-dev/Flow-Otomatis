# TASKS — Flow-Otomatis

## STEP 08 — Repository Foundation
Status: PASS.

## STEP 09 — App Shell/UI Implementation
Status: PASS.
- Last tested STEP 09 SHA: ee90740ba6e620af1107d73b19b6753395aa26bd.
- Final STEP 09 CI: 37587748975 — SUCCESS.
- 30/30 frozen UI visual gate: PASS.

## STEP 10 — Minimum End-to-End Vertical Slice
Status: PASS.

### S10-T01 — Import Contract + Domain Readiness
- Status: PASS.
- FLOW_OTOMATIS_IMPORT.json v1.0 typed contract.
- SCENE_### uniqueness and fixed production profile enforced.
- Target <=10 seconds enforced.
- 4/6/8/10 recommendation recomputed from Target.
- Real readiness states derived from validated inputs.

### S10-T02 — Safe Package Reader + SQLite Workspace Persistence
- Status: PASS.
- ZIP/directory/manifest import supported.
- ZIP traversal and unsafe archive path rejection verified.
- Approved-image existence and motion-prompt evidence resolved.
- Per-project SQLite save/reload verified.

### S10-T03 — Real Import / Validation / Workspace UI
- Status: PASS.
- Frozen import button wired to real file selection.
- Real package data appears in frozen validation screen.
- Workspace creation persists state.
- Frozen Workspace and Scene dock render real state.
- No UI redesign and no direct presentation-layer persistence/filesystem ownership.

### S10-T04 — Regression / Windows Evidence
- Status: PASS.
- Last tested implementation SHA: 64903913e83cbb9d86909b0c1c255585b2295351.
- Final CI run: 37590300417 — SUCCESS.
- Ruff format/lint: PASS.
- mypy strict: PASS.
- architecture guard: PASS.
- pytest: 32 passed.
- UI regression: 30/30 PASS; similarity 0.6344–0.9643 at threshold 0.55.
- UI evidence artifact ID: 11468740474.
- Windows artifact ID: 11468466375.
- Windows artifact SHA-256: 5372cc919f7194085705e920eddcacff2d6654eef5e5ff9a2cae9268ede1e83d.
- Portable EXE smoke: PASS.
- Live Google Flow: NOT TESTED.

## NEXT — STEP 11: Feature Implementation Waves
Status: READY, NOT STARTED.

Software Factory rule:
- implement backlog through small cohesive waves;
- each wave requires explicit acceptance criteria and regression evidence;
- do not combine the complete backlog into one giant change;
- integrations/external services belong to STEP 12.

### W11-01 — Scene Planning & Readiness
- Status: READY.
- Priority/Risk: P0 / MEDIUM.
- Goal: make local Scene planning truly editable/persistent before provider integration.
- Scope:
  - user-selected Flow duration 4/6/8/10 persisted per scene;
  - selected duration cannot be shorter than Target;
  - Target cannot be rewritten by normal planning actions;
  - real image rescan/remap status;
  - recompute scene readiness after local changes;
  - frozen Workspace/Scene Inspector controls invoke application commands;
  - persistence/reload and UI regression evidence.
- Out of scope:
  - live Google login;
  - live Flow submit/generation;
  - live Flow download;
  - Gemini API.
- Acceptance:
  - edit → persist → restart/reload keeps valid duration selection;
  - invalid shorter duration is blocked;
  - image rescan updates readiness deterministically;
  - 30 frozen UI fixtures remain regression-green.

### W11-02 — Local Project Hub / Recent Project / Recovery
- Status: PLANNED after W11-01.
- Goal: replace remaining local Project Hub/recovery fixtures with persisted project metadata and recovery state.

### W11-03 — Local Queue / Job State Engine with Fake Provider
- Status: PLANNED after W11-02.
- Goal: implement durable serial R1 queue/state transitions against a fake provider only.
- External live provider adapter remains STEP 12.

### W11-04 — Local Results / Handoff Manifest
- Status: PLANNED after W11-03.
- Goal: real local result state and FLOW_OTOMATIS_RESULT.json generation using fake/fixture job outcomes.

Do not start STEP 11 until the product owner says "lanjutkan".
