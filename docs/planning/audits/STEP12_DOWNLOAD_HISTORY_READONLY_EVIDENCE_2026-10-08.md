# SOL STEP 12 — SQLite Download History Read-Only Regression

**Date:** 8 October 2026 WIB
**Repository:** `inoriko920-dev/Flow-Otomatis`
**Disposition:** **COMPLETE / PASS**, offline application + official GitHub Windows CI.

## Confirmed issue
In the canonical `SqliteDownloadResultRepository`, both `get()` and `list_for_episode()` opened existing project SQLite databases in read-write mode and executed `CREATE TABLE IF NOT EXISTS download_results` just to query Download history. For legacy imported projects without that table, opening Hasil could mutate the source `project.sqlite3` while merely viewing it. This violated the precedent of the workspace repository's read-only legacy-project reads.

## Implemented behavior
- Only file `src/flow_otomatis/infrastructure/persistence/sqlite_download_result_repository.py` was changed in production.
- Existing DBs are now opened using SQLite URI `mode=ro`, with no schema DDL or transaction mutations in `get()` and `list_for_episode()`.
- `sqlite_master` determines whether the history table exists. For legacy DBs without `download_results`, read returns `None` or `()` and **does not create the table**.
- Missing project DB remains missing, no implicit directory/database creation. Existing `download_results` rows still decode as before.
- Corrupt database read still raises existing `StorageError`, with no attempted repairs.
- Explicit write methods `save()` and `save_failure_if_unconfirmed()` retain existing behavior and may create the history table as needed.
- No new port, SQL migration, schema version, product UI, login, browser, media download or provider changes.

## New integration tests
`tests/integration/test_download_repository_readonly.py`:
1. A real legacy project database with unrelated table and no download_results is queried repeatedly; raw SQLite SHA-256 and length remain identical, download_results stays absent and no journal is produced.
2. Missing project database remains absent after both queries.
3. Pre-existing legitimate DOWNLOADED record round-trips through both readers without changing the raw SQLite SHA-256 or creating a journal.
4. Corrupt SQLite source raises existing `StorageError`; bytes and SHA-256 remain unchanged.

## CI and release proof
- Pull request: https://github.com/inoriko920-dev/Flow-Otomatis/pull/21 — squash merged to `main`.
- **Exact CI-verified main source SHA:** `936279f71d1a2863a5b9a0f61923d9b226c1b0a2`.
- Official main CI: https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37732145080 — **SUCCESS**, all three jobs, exact `head_sha = 936279f71d1a2863a5b9a0f61923d9b226c1b0a2`.
- Quality job `113163462226`: Python 3.14.7 locked uv, Ruff format/lint, mypy 81 source files, architecture check PASS; **227 pytest passed**.
- Frozen UI job `113163722492`: **30/30 PASS** against frozen approved reference.
- Windows portable job `113163937582`: Playwright Chromium staged/smoke, portable PyInstaller ZIP build, executable smoke, full distributable ZIP checksum, CRC, path and source-SHA validation **PASS**.
- Inner distributable ZIP: **1,049 entries**, SHA-256 `480ef6a8c08036990cf458b8f0c0ec2971aa47a031b29ea12112a461c3f357b6`, source `936279f71d1a2863a5b9a0f61923d9b226c1b0a2`.
- GitHub Actions **outer artifact wrapper**: ID `11530112083`, size `435,727,200` bytes, SHA-256 `789bb3c1afd5106580180f9b288e4067665b203e5477519ff291f6a8c02e9056`, expires `2026-10-22T05:28:39Z`.
- UI evidence outer artifact: ID `11529962022`, `3,316,911` bytes, SHA-256 `8c5e7660bd9594f9a6432c197affbaa0cfa89512328875a35e50c75fc0426ab8`, expires `2026-10-22T05:25:20Z`.
- Outer GitHub artifact SHA-256 is not the same as the inner distributable ZIP SHA-256; artifacts are temporary, not full independent backups.

## Scope limits and gate
- This verifies file/database integrity under offline/Windows CI, **not live Google Flow behavior**.
- User previously reported Google login working; owner-side READY after fully restarting Flow-Otomatis / `Validasi restart: Lulus` has not been independently demonstrated. Live one-Scene Generate and Download remain BLOCKED / NOT TESTED.
- ASTRA R00–R04 B01–B06 remain CLOSED at offline boundaries. Original STEP 12 source-of-truth, frozen UI and previous evidence remain unchanged.
- This evidence is committed **after** the tested code SHA as a docs-only follow-up; do not mistake docs commit for a new tested source SHA.
