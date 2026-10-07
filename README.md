# Flow-Otomatis

Flow-Otomatis is a Windows 11 desktop application project for deterministic scene-based Google Flow production orchestration.

## Software Factory status
- STEP 00–08: completed through Repository Foundation.
- STEP 08: **PASS**.
- Next: **STEP 09 — App Shell/UI Implementation + screenshot actual vs frozen reference**.
- Live Google Flow has **NOT** been tested yet; that belongs to later integration work.

## Foundation verified on Windows
- CPython 3.14.7.
- PySide6 6.11.2.
- Playwright 1.63.0 with staged Chromium smoke.
- Pydantic 2.13.5.
- keyring 25.7.0.
- PyInstaller 6.22.3 onedir portable build.
- Ruff / mypy / pytest / architecture guards.
- GitHub Actions windows-2025.

## Frozen product rules
- Windows 11 x64, portable multi-file ZIP.
- Indonesian-first desktop UI.
- Biography production lock: Omni Flash 1.1 • 720p • 16:9.
- Audio/SRT Target Duration remains authoritative.
- Flow generation duration is 4/6/8/10; app recommends, user confirms valid choice.
- Approved reference image auto-mapped by canonical SCENE_###.
- Generate and Download are separate.
- No CAPTCHA/MFA bypass, credential export, hidden account rotation, or quota/rate-limit evasion.

## Source of truth
Before modifying implementation, read:
1. AGENTS.md
2. PROJECT_STATE.md
3. TASKS.md
4. docs/software_factory/
5. docs/planning/
6. docs/ui/
7. docs/architecture/
8. docs/adr/
9. docs/handoff/current/

STEP 09 must implement against the frozen UI reference; silent redesign is forbidden.
