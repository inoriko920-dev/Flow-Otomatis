# STEP 12 — Hasil error recovery audit and handoff

Date: 2026-10-08 12:41:00 WIB
Repository: inoriko920-dev/Flow-Otomatis
Baseline: b7c731c (main). Branch: fix/results-error-recovery-20261008.
Authorization: product owner requested a bug audit and immediate fixes on this repository.

## Confirmed defects
1. Hasil navigation called the results snapshot without a UI error boundary. Unreadable SQLite history raised into Qt's event loop with no user-facing recovery message.
2. Download row timestamp/take decoding leaked ValueError instead of the existing typed storage error; get and list were both affected.
3. The editing-handoff button directly called the export operation. A publication PermissionError escaped into Qt and left the previous export-success path in memory.

## Changes
- Reuse MainWindow's existing navigation and export owners; no alternate service, schema, dependency or screen.
- Keep failed Hasil navigation on the previous view/navigation selection and retain Agent context. Show a static Indonesian recovery message without raw exception/path details.
- Map download-row decode failures to existing WorkspaceCorruptError. Preserve read-only SQL and original bytes; do not repair records or discard history.
- Add a UI-only export callback for known application/OS failures. Direct programmatic export still raises errors; clear the success marker before each attempt and set it only on success.
- Existing atomic manifest writer remains unchanged; prior manifest survives failed publication and retry remains explicit via the same button.

## Reproduction and local evidence
- Baseline full suite: 227 passed.
- New tests failed on unpatched code: navigation callback exceptions (corrupt SQLite, bad download timestamp, bad take), export callback PermissionError, and both repository read APIs leaking decode errors.
- Fixed focused suite: 12 passed. Full unit/contract/integration/smoke/UI suite: 233 passed on CPython 3.14.8/Linux with QT_QPA_PLATFORM=offscreen.
- Ruff format/lint and architecture guard PASS.
- Mypy Windows-target validation: see final CI update. Default Linux-target mypy reports four existing winreg attribute errors in system_chrome_cdp.py; application targets Windows and no dependency/config change was made to hide them.
- Windows CI/build and frozen visual comparison pending at commit creation. No real Google login/Generate/Download performed.

## Handoff
Active step remains STEP 12; offline local bug repair only. Live restart-validation gate unchanged.
Next exact action: run official PR Windows CI (quality, 30-state UI comparison, portable build/smoke); merge only after passing, then record exact run/SHA.
Scope has no migration, contract change, UI refreeze or new architecture decision requiring planning DOCX.
