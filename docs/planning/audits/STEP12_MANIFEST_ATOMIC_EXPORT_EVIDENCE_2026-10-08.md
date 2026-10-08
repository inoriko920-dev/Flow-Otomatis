# SOL — STEP 12 Independent Manifest Export Race Hardening
Date: 8 October 2026 WIB
Status: **COMPLETE / PASS** (OFFLINE / official Windows CI)
Repo: `inoriko920-dev/Flow-Otomatis`
Scope: result handoff JSON write alone, not live Google Flow.

## Finding / prechange behavior
`src/flow_otomatis/infrastructure/filesystem/result_manifest_writer.py` previously used one static `FLOW_OTOMATIS_RESULT.json.tmp` path for every concurrent export. When two calls interleaved, the second could replace a temp file before the first called `os.replace`; the first then raised `FileNotFoundError` or otherwise interfered with the other attempt. A failed publish could leave an orphan .tmp beside a valid pre-existing manifest.

## Corrective implementation
- Each `ResultManifestWriter.write` attempt creates a uniquely owned `tempfile.NamedTemporaryFile` under the same project `exports/` directory, with no global mutable lock or database change.
- Serialize original v1.0 schema, write/flush/fsync and close before `os.replace(temporary, FLOW_OTOMATIS_RESULT.json)`.
- Cleanup only the current attempt's temp file in a `finally` guard on both success and failure. Never remove the previously published final manifest on a failed write, fsync or rename.
- Concurrent exports may still finish in either order (**last successful publisher wins**). This fix guarantees no shared temporary-file collision or invalid intermediate published JSON; it does NOT add optimistic version fencing against a logically older snapshot.
- Prior R03 availability verification before writing and v1.0 `UNAVAILABLE` semantics are unchanged. This work does not prove compatibility of external strict-enum consumers.
- UI, download files, session keys, browser worker and Google Flow live behavior untouched.

## Deterministic regressions
`tests/integration/test_result_manifest_atomic_writes.py`:
1. Two real concurrent writers with a `threading.Event` barrier around the first `os.replace`: both return successfully; unique temporary names and valid final JSON; no orphan `.tmp` remains. This is deliberately a race that the old fixed-temp writer fails.
2. Injected `OSError` during `os.replace`: old valid manifest bytes remain identical, failed attempt temp removed.
3. Injected partial write failure: old published bytes remain identical, failed temp removed.

## Verified merge and CI
PR [#19](https://github.com/inoriko920-dev/Flow-Otomatis/pull/19) squash merged.
Exact merged/tested `main` implementation SHA: `42afad61a6bde7798623d807de2c74c51339fe82`.
Official fresh `main` CI: https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37729402213, all three jobs **SUCCESS**:
- quality `113154864681`: Python 3.14.7, uv frozen, Ruff format/lint, mypy 81 source files and architecture PASS, **220 pytest passed**.
- ui-visual `113155175319`: **30/30 approved frozen states PASS**.
- package-windows `113155343456`: Chromium staged/smoke, onedir PyInstaller ZIP, portable executable smoke, final ZIP SHA-256/CRC/Windows path/source verifier **PASS**.
- Actual distributable ZIP has **1,049 members**, internal ZIP SHA-256 `242beb868acf5d2e190ba0f746963d607b1493aea258b34213d84fa2714da97d`, manifest source SHA `42afad61a6bde7798623d807de2c74c51339fe82`.
- GitHub artifact ID `11529730338`, name `Flow-Otomatis-step12-i12-01-restart-proof-win-x64`, outer wrapper SHA-256 `ccf0aa7d64ddb967d5732952970aa7785f140fa8f579f4906659869b4d9b7272`, archive size 435,726,215 bytes, expires `2026-10-22T04:54:24Z`. Outer wrapper digest differs from inner distributable ZIP.
- Frozen-UI artifact ID `11529167915`, outer wrapper SHA-256 `14f60430bb1efc94e9879390cd8d3f02cc5dc948ebc4c91030566008f2129c6d`, expires `2026-10-22T04:52:12Z`.

## Important boundaries
- New ASTRA B01–B06 R00–R04 remain locally CLOSED/PASS. This improvement is independent after that audit.
- User said Google login works. **Same-profile READY after closing/reopening Flow-Otomatis and `Validasi restart: Lulus` remains UNVERIFIED**.
- I12-02B2-LIVE one-Scene Google Flow submit and I12-03-LIVE download are still BLOCKED; no live login, secret, token, Generate/Download mutation or UI redesign happened.
- GitHub Actions artifacts expire and do not replace a 100% source backup.
- This documentation closeout commit is docs-only and not part of the CI-tested code SHA above.
