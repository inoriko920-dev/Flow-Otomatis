# SOL integration: 22 UIX offline states + Google session / Flow preflight (2026-10-09)

## Source provenance and scope
- Native UIX22, local Workspace source: PR #31 `c4552afa867be1c51f9a376215f6eb803ad15d9e`.
- Google current-instance session freshness, single-thread read-only Flow navigation, migrated `flow.google.com` official host, Qt callback fencing: PR #32 `1d9a10c81834f189d46a06dc01958c0a5a2971b6`.
- Isolated integration branch includes both source snapshots without merging PRs to `main` or mutating source branches.
- The 2 collision paths `src/flow_otomatis/bootstrap/main.py` and `src/flow_otomatis/presentation/main_window.py` were surgically merged to preserve UIX22/Workspace and session/Flow additions. All 13 non-overlapping paths reuse PR #32 Git blobs.
- New 22 UI states are **offline simulation preview** accessed from an imported local Workspace with **Pratinjau 22 UI Multiakun (Simulasi)**; they do not replace all seven static shell routes or enable live multi-account production.
- Google Profile maintains manual login, **Cek Ulang Sesi**, read-only **Cek Akses Flow**; public site reachability never confirms account identity/workspace.
- CI gates: Windows quality, frozen UI visual references, offline simulator, UIX22 EXE, Windows packaged main application. Manual Chrome identity/workspace/restart checks pending.
- Never submit live Generate/Download or spend credits, and do not merge to `main` or release without owner approval.
