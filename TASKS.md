# TASKS — Flow-Otomatis

## S08-T01 — Documentation Source-of-Truth Bootstrap
- Owner: SOL
- Status: PASS after binary verification
- Priority/Risk: P0 / HIGH
- Result: mandatory planning/reference DOCX + Software Factory guide + UI reference + governance are in repo before source code.

## S08-T02 — Repository Skeleton + Quality Tooling
- Owner: SOL
- Status: READY
- Priority/Risk: P0 / MEDIUM
- Scope: pyproject.toml, uv.lock, minimal canonical packages, minimal bootstrap import path, tests layout, architecture checker, Ruff/mypy/pytest configuration, compatibility pin evidence.
- Out of scope: product screens/features, live Google Flow automation, full persistence schema, production provider integration.
- Acceptance: locked environment resolves; imports valid; architecture/lint/type/unit-contract skeleton gates pass.

## S08-T03 — Windows CI + Portable Foundation Smoke
- Owner: SOL
- Status: NOT READY until S08-T02 PASS
- Scope: windows-2025 CI, frozen install, minimal PyInstaller onedir packaging, path/resource startup smoke.
- Live Google Flow: NOT TESTED in normal CI.
