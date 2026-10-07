# HANDOFF — STEP 12 AUDIT A01 → A02

## Gate
A01 — Import integrity and data linkage: **PASS**.

This handoff covers the audit-remediation track inside STEP 12. It does not supersede the existing live-integration gate and does not unblock I12-02B2-LIVE.

## Verified baseline
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- A01 implementation merge: `865e92f4a3da01a35339203f263ab938a420d3bd`
- Main CI: `37644208386` — SUCCESS
- Quality: `112870617392` — SUCCESS
- UI visual: `112871584570` — SUCCESS
- Windows package: `112872148801` — SUCCESS
- pytest: 95 passed
- mypy: 63 source files
- UI: 30/30 PASS
- Playwright Chromium smoke: PASS
- portable smoke: PASS

## A01 closed
F01:
- missing prompt `.txt` in ZIP/folder is a typed validation error;
- it cannot become literal READY prompt content;
- failed validation happens before workspace persistence.

F02:
- imports create; Scene planning updates;
- duplicate episode create is atomic under SQLite write locking;
- duplicate import cannot overwrite the persisted project/Scenes;
- prior jobs/downloads remain untouched;
- concurrent creates cannot both succeed;
- UI reports the duplicate safely in Indonesian.

Evidence:
- `docs/planning/audits/A01_IMPORT_INTEGRITY_EVIDENCE_2026-10-07.md`

## Findings still open
- F03 — queued request revision/readiness consistency.
- F04 — corrupt Scene row can break project listing.
- F05 — Google session checking blocks the Qt event path.
- F06 — orphan RUNNING jobs lack real recovery classification.

## Next package — A02 only
Audit source requires A02 to close F04.

Owners:
- `SqliteWorkspaceRepository`;
- `ProjectLibraryService`;
- Project Hub / its safe presentation path.

Required behavior:
- validate database row decoding at the canonical SQLite read boundary;
- map invalid enum, numeric, or timestamp data to `StorageError` or a clear corrupt-data subtype rather than leaking raw `ValueError`/conversion exceptions;
- `list_recent` must isolate one corrupt project so healthy projects remain available;
- opening a specific corrupt project must produce a safe, truthful error;
- Project Hub must honestly surface that a project is corrupt/unavailable without crashing the Qt callback;
- reading/recovery discovery must not modify, delete, or silently repair the corrupt source database;
- do not create a competing storage helper; keep the canonical repository path.

Primary regression files:
- `tests/integration/test_project_library_wave.py`;
- `tests/ui/test_project_hub_recovery.py`.

A02 acceptance:
- one healthy + one corrupt project still leaves the healthy project openable;
- invalid readiness enum and invalid timestamp are isolated;
- specific corrupt-project open returns a safe typed error;
- source corrupt DB bytes/state are not mutated merely by listing/open attempts;
- tests distinguish behavior of direct `load` from resilient `list_recent`.

Do not implement A03 in the same package.

## Safety/product boundary
- no frozen UI redesign;
- no deletion or auto-repair of corrupt project databases;
- no live Flow provider activation;
- Flow 4/6/8/10 and Audio/SRT Target rules remain frozen;
- I12-02B2-LIVE remains BLOCKED.

## Instruction to next SOL
After the product owner says `lanjutkan`, verify `main` still descends from the A01 baseline, inspect F04 against current code, implement only A02, run targeted + complete Windows CI, update evidence/state/handoff, then stop before A03.
