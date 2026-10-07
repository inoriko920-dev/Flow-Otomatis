# TASKS — Flow-Otomatis

## S08-T01 — Documentation Source-of-Truth Bootstrap
- Owner: SOL
- Status: BLOCKED
- Priority/Risk: P0 / HIGH
- Goal: place complete STEP00–07 planning, Final UI Reference, final UI images, architecture/handoff and AI governance in repo before source code.
- Work completed:
  - repository initialized with documentation guard;
  - AGENTS/STATE/PLAN/TASKS + architecture/governance text committed;
  - source-of-truth binary hash manifests committed;
  - Software Factory guide added to required manifest;
  - repo-ready binary pack prepared with 47 entries;
  - upload pack SHA-256: 7f14ee5a877d041daa08a486628f8541d62fe1ecffdd20cd8b2230a28b56f107;
  - ZIP integrity PASS.
- Blocker: current connected GitHub writer has no direct binary DOCX/PNG upload path.
- Acceptance still missing: actual mandatory binary DOCX/PNG/ZIP files present at canonical repo paths and hash-verified.
- Out of scope until PASS: src/, dependencies, CI feature build, provider code.
- Next: transfer/extract binary pack to canonical repo paths and verify hashes.

## S08-T02 — Repository Skeleton + Quality Tooling
- Status: NOT READY — blocked by S08-T01.
- Planned: pyproject.toml, uv.lock, minimal canonical packages, Ruff/mypy/pytest, architecture checker.
- Do not start before S08-T01 PASS.

## S08-T03 — Windows CI + Portable Foundation Smoke
- Status: NOT READY.
- Depends on S08-T01 + S08-T02 PASS.
