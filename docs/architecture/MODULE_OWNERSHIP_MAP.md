# MODULE OWNERSHIP MAP

- bootstrap: app composition/startup/shutdown only.
- presentation: Qt shell/screens/dialogs/components/models/theme; no DB/filesystem/browser/provider calls.
- application: commands/queries/services/ports/events; orchestration only.
- domain: project/scene/jobs/profiles/results/errors; pure business rules.
- contracts: package/worker/provider schemas and boundary DTOs.
- infrastructure/persistence: SQLite repositories/migrations/connections.
- infrastructure/filesystem: PathService, safe package I/O, atomic I/O.
- infrastructure/secrets: keyring-backed secret store.
- infrastructure/browser/flow_web: Flow-specific locators/page objects/provider implementation.
- workers/browser: Playwright process/event-loop/session lifecycle.
- infrastructure/ai/gemini: Gemini provider implementation only.
- application/services: AI agent orchestration and job orchestrator.
- infrastructure/diagnostics: structured logs/redaction/export.
- resources: shipped runtime icons/styles/licenses only.
- scripts: build/check/staging/smoke automation, not product logic.
- tests: behavior evidence at correct boundary.
- docs: source-of-truth planning/UI/architecture/ADR/handoff.
