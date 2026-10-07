# HANDOFF STEP 08 → STEP 09

## Gate
STEP 08: **PASS**

## Repository evidence
- Source-of-truth binary commit: `af1ac445abcaee4eadc5be1f0875761d789368f9`
- Foundation skeleton commit: `32b9e01fdacf049465f1612132605f552d61751a`
- Dependency lock commit: `9c496506dbc35ddfca0f793c847e35e4b7ccb0cc`
- Last tested implementation SHA: `539ffb8e25a2f52492a6fbf3de4df805ca670742`

## Test evidence
### S08-T02 Foundation Lock
Run `37583227824`: SUCCESS.
- Python 3.14.7
- lock resolve/sync PASS
- Ruff PASS
- mypy PASS
- architecture guard PASS
- unit/contract tests PASS
- uv.lock committed

### S08-T03 Final CI
Run `37583870436`: SUCCESS.
- quality job PASS
- Chromium staging PASS
- Playwright local browser smoke PASS
- third-party inventory PASS
- PyInstaller onedir build PASS
- portable EXE smoke from foreign Unicode/space CWD PASS
- artifact upload PASS

Artifact:
- name: `Flow-Otomatis-foundation-win-x64`
- ID: `11465692132`
- portable ZIP size: `387634259` bytes
- SHA-256: `c8c000c59fe0beb4d4df961d7b348096fa3b15402b87ab5a43c20b79c22c1e1b`
- downloaded artifact outer ZIP integrity: PASS
- checksum inside artifact: MATCH

## Frozen UI source
Read:
- `docs/ui/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx`
- `docs/ui/IMPLEMENTATION_OVERRIDES.md`
- `docs/ui/prompts/UI_PROMPT_BATCHES_V1_2.md`
- STEP 05 Product Blueprint.

## STEP 09 exact purpose
**App Shell/UI Implementation + screenshot actual vs frozen reference**

SOL must:
1. implement the production App Shell/UI from the frozen reference pack;
2. preserve navigation/state/copy/interaction decisions;
3. generate ACTUAL screenshots in CI/test fixtures at the required reference viewport/state;
4. compare ACTUAL with REFERENCE semantically/visually;
5. fix implementation drift rather than silently redesigning the frozen reference;
6. keep provider/live Google Flow integration out unless STEP 09 explicitly needs a fake/stub to render a UI state.

## Architecture boundaries
- presentation → application → domain
- infrastructure implements ports
- Browser Worker owns Playwright
- bootstrap is composition only
- no UI direct DB/filesystem/browser/provider SDK access

## Important NOT TESTED
Real Google Flow live generation/login/download remains NOT TESTED and is not a STEP 09 success claim.

## Next exact action
Wait for product owner command `lanjutkan`, then start STEP 09 only.
