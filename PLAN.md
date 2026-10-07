# PLAN — Flow-Otomatis

## Stable sequence
1. S08-T01 Documentation Source-of-Truth Bootstrap.
2. Gate: verify all planning DOCX, Final UI Reference, 30 final PNG UI references, architecture/code-constitution handoff, governance files and hashes.
3. S08-T02 Repository Skeleton + Quality Tooling.
4. S08-T03 Windows CI + Portable Foundation Smoke.
5. Continue later Software Factory implementation steps only after their gates.

## Non-negotiable
Production coding cannot begin while S08-T01 is not PASS.

## Architecture target
- Modular monolith.
- presentation -> application -> domain.
- infrastructure implements ports.
- Browser Worker owns Playwright.
- bootstrap is composition only.
