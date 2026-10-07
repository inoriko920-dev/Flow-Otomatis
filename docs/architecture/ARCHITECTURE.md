# Flow-Otomatis Architecture — STEP 06

Status: PASS_WITH_PROVISIONAL

## Chosen architecture
- Modular monolith desktop + ports/adapters + dedicated Browser Worker process.
- CPython 3.14.x x64 standard build.
- PySide6 / Qt 6 Widgets + Model/View.
- Playwright Python + bundled Chromium; persistent context per authorized profile.
- SQLite global app DB + per-project DB + JSON interchange manifests.
- Windows Credential Locker via keyring; browser session dirs under user LocalAppData.
- PyInstaller onedir -> portable multi-file ZIP.
- pyproject.toml + uv.lock.
- Ruff + mypy + pytest + pytest-qt.
- GitHub Actions Windows runner; live Google Flow is NOT TESTED by normal CI.

## Dependency direction
presentation -> application -> domain/contracts <- infrastructure
Browser Worker owns Playwright/Chromium and does not write project SQLite directly.

## Core invariants
- Audio/SRT Target is authoritative.
- Approved image auto-mapped by SCENE_###.
- Flow duration is one of 4/6/8/10 and user-confirmed.
- Generate and Download are separate.
- Ambiguous external submit/result is never blindly resubmitted.
- No secrets in repo/project package/normal logs/diagnostics.
- No CAPTCHA/MFA bypass or quota/rate-limit evasion.
- R1 generation concurrency = 1.
