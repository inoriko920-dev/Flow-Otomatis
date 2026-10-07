# TASKS — Flow-Otomatis

## S08-T01 — Documentation Source-of-Truth Bootstrap
- Owner: SOL
- Status: BLOCKED
- Priority/Risk: P0 / HIGH
- Goal: place complete STEP00–07 planning, Final UI Reference, final UI images, architecture/handoff and AI governance in repo before source code.
- Work completed:
  - repository initialized with documentation guard;
  - AGENTS/STATE/PLAN/TASKS and architecture/governance text being committed;
  - source-of-truth binary hash manifests added.
- Blocker: current connected GitHub writer has no direct binary DOCX/PNG upload path.
- Acceptance still missing: actual mandatory binary DOCX/PNG files present and hash-verified in repo.
- Out of scope until PASS: src/, dependencies, CI feature build, provider code.
- Next: upload/verify binaries when a supported binary GitHub write path is available.

## S08-T02 — Repository Skeleton + Quality Tooling
- Status: NOT READY — blocked by S08-T01.
- Planned: pyproject.toml, uv.lock, minimal canonical packages, Ruff/mypy/pytest, architecture checker.
- Do not start before S08-T01 PASS.

## S08-T03 — Windows CI + Portable Foundation Smoke
- Status: NOT READY.
- Depends on S08-T01 + S08-T02 PASS.
