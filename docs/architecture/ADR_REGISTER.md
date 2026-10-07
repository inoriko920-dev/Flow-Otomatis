# ADR Register — STEP 06

- ADR-001 ACCEPTED: modular monolith + ports/adapters.
- ADR-002 ACCEPTED: CPython 3.14.x x64.
- ADR-003 ACCEPTED: PySide6 Qt Widgets + Model/View.
- ADR-004 ACCEPTED: global + project SQLite plus JSON interchange.
- ADR-005 ACCEPTED: Qt main thread + local I/O workers + dedicated Browser Worker + serial R1 queue.
- ADR-006 ACCEPTED: Playwright bundled Chromium, deterministic FlowWeb adapter/page objects.
- ADR-007 ACCEPTED: Gemini behind provider boundary; AI tools invoke application commands with approval for material actions.
- ADR-008 ACCEPTED: PyInstaller onedir portable ZIP + PathService + LocalAppData.
- ADR-009 ACCEPTED: uv lock + Ruff + mypy + pytest/pytest-qt + Windows CI + fake provider.
- ADR-010 ACCEPTED: Windows Credential Locker/keyring; browser sessions user-scoped.
- ADR-011 ACCEPTED: no FFmpeg in R1.
- ADR-012 ACCEPTED: no global undo; previews + transactions + audit.
- ADR-013 PROVISIONAL: optional paid official API only after explicit scope.
- ADR-014 PROVISIONAL: exact dependency versions after Windows compatibility spike.
- ADR-015 ACCEPTED FOR A01: atomic workspace create rejects duplicate identity; legitimate updates remain explicit update semantics.
- ADR-016 ACCEPTED FOR A03: coherent request revision/fingerprint plus durable job owner/lease and transactional orphan recovery.
- ADR-017 IMPLEMENTED + VERIFIED IN A04: all Playwright/CDP lifecycle stays on one Browser Worker owner; Qt communicates through non-blocking command/result boundaries.

## Current-auth clarification
ADR-006 remains applicable to automated browser-adapter work, but it does not override the later STEP 12 normal-Chrome authentication decision recorded in PROJECT_STATE and the current handoff. Human Google sign-in uses installed normal Chrome with no Playwright/CDP attachment; automation attaches only after authentication.
