# SOL STEP 12 — Late Download Failure History Protection
8 October 2026 WIB • `inoriko920-dev/Flow-Otomatis`
**Outcome: COMPLETE / PASS — offline and Windows CI only.**

## Concrete bug and scope
`LocalResultsService.record_download_failed` previously called the general unconditional `DownloadResultRepositoryPort.save(record)`. This could overwrite a confirmed `DOWNLOADED` record, its local output path and take if a delayed previous attempt emitted a FAILED outcome afterward. This path bypassed the atomic `save_failure_if_unconfirmed` operation already introduced by R03 into `SqliteDownloadResultRepository`.

Only `src/flow_otomatis/application/services/local_results.py` changed in production. Failure reports now call the existing atomic `save_failure_if_unconfirmed`, then read back and return the effective saved row instead of falsely reporting FAILED when a previously confirmed DOWNLOADED remains. New download failures without confirmed success are still saved. No port/schema/migration, UI, Generate provider, login, Google Flow live, remote account, browser/session or filesystem write contract was changed.

## New real SQLite regression
`tests/integration/test_local_results_wave.py`:
- Recorded local nonempty video + GENERATED remote ID survives a subsequent late `record_download_failed` exactly (state, path, timestamp, take, usable Hasil handoff, v1 manifest status).
- Initial failed download without a successful record is persisted and displayed as FAILED, with handoff disabled.
- Second independent `LocalResultsService` using separate SQLite repository connections sends a delayed failure; the recorded success remains intact. Deterministic `threading.Event` barrier makes ordering repeatable.

Tests do not claim to have run a live Google download; real temporary SQLite/file objects are used.

## Verified official GitHub events
PR [#20](https://github.com/inoriko920-dev/Flow-Otomatis/pull/20) squash-merged. Exact tested **main implementation SHA**: `8149309540233a3a9255b6a2610cfb2554937ed1`.
Official main CI https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37730824287 — **SUCCESS**, all three jobs:
- `quality` job `113159305703`: locked Python 3.14.7/uv; Ruff formatter/lint PASS, mypy 81 source files PASS, architecture PASS; **223 pytest passed**.
- `ui-visual` job `113159580981`: approved frozen UI **30/30 PASS**.
- `package-windows` job `113159789601`: staged Chromium/smoke, Windows portable PyInstaller onedir build, executable portable smoke, checksum/CRC/path/source ZIP validation all PASS.
- Distributable ZIP: 1,049 entries; **inner ZIP SHA-256** `07bd9418bd37eea491e58484650b5e674df18773b0e711343ad187c629bdfb5c`, manifest source SHA `8149309540233a3a9255b6a2610cfb2554937ed1`.
- Temporary Windows GitHub artifact ID `11529054245`, 435,725,963 bytes, **outer GitHub wrapper SHA-256** `a3254d36eafc023647908f790ecc693fdb43e01793fd096aeea502cdb5ecf1c5`; expiration `2026-10-22T05:12:25Z`.
- Frozen UI evidence artifact ID `11530065507`, 3,316,911 bytes, SHA-256 `d56522ae57920c23665e3fd73f571c5e49fa8b1e3e73a04964feb222af8c49ac`, expiration `2026-10-22T05:09:36Z`.
- The outer workflow artifact archive and its inner distributable ZIP are DIFFERENT byte streams; their SHA-256 values must not be confused. GitHub artifacts are expiring, not a full off-platform source backup.

## Product gate / limits
ASTRA R00–R04 B01–B06 remains OFFLINE PASS. User said manual Google login works, but no verified `READY` after fully closing and restarting Flow-Otomatis or `Validasi restart: Lulus` was received. Live I12-02B2-LIVE Generate and I12-03-LIVE Download remain **BLOCKED and NOT TESTED**. No credentials/session/token, live account operations, UI redesign or product schema changes in this slice.

This document commit is documentation-only, after the CI-tested implementation SHA listed above.
