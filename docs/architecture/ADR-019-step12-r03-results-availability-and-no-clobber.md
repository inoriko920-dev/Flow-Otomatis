# ADR-019 — STEP 12 R03 effective media status and no-clobber file publication
Date: 8 October 2026 WIB
Status: IMPLEMENTED / OFFLINE REGRESSION VERIFIED in PR #16
Source: ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-08.docx, ADR-018.
Code merge SHA: `1f82675eb6282a3f5070c4320c5898a4304dd516`; tested source SHA: `17dc2be0c7e4c69a99ab5129ea311492a182ecc4`.

## B04: history vs current physical availability
- `DownloadRecord.state=DOWNLOADED` remains the immutable historic fact; physical availability is derived afresh at `LocalResultsService.snapshot` and in `ResultManifestWriter.write`, independently.
- Only absolute, readable, regular, nonempty files qualify; requires a successful read of the first byte. Missing/directory/zero-byte/access-denied all result in effective `DownloadState.UNAVAILABLE`.
- `ProjectResults.downloaded_count` excludes UNAVAILABLE; attention increments and `handoff_ready` stays false. Frozen Hasil shows "Tidak Tersedia".
- Existing `FLOW_OTOMATIS_RESULT.json` schema_version **1.0** retained. For unavailable files, scene `download_status="UNAVAILABLE"` rather than falsely exporting `DOWNLOADED`; field names, scene structure and remote_result_id unchanged. Consumers that enforce a closed enum of historic states may need to learn `UNAVAILABLE` (external consumer compatibility has NOT been independently certified). This is a conservative status extension, not a proof all third-party readers accept it.
- Historical download database rows/Generate identity and prior output path are retained; no auto redownload/repair/regeneration.

## B05: publish atomically without clobber
- Browser driver is given a `<final-name>.<random-UUID>.part` absent path in the same destination folder; each attempt owns only that path.
- After driver confirms nonempty own partial, publish via Python `os.link(partial, final)`, backed by CreateHardLinkW on Windows NTFS and same-filesystem hardlink on POSIX. A final file already created—even during the driver callback—causes an atomic failure, never an overwrite. Destination path is not resolved through existing final-file symlinks. No `os.replace`/unsafe copy fallback.
- On collision, keep existing final and own partial for operator inspection. On successful publish, unlink own partial best effort only; inability to unlink does not invalidate a confirmed final.
- On unsupported filesystem or unexpected publication failure, fail closed with `MediaDownloadAmbiguousError`, keeping partial and prohibiting automatic retry. Not all network shares support atomic hardlinks. No live Flow driver/selector wired here.
- A concurrent losing attempt may emit FAILED, but `SqliteDownloadResultRepository.save_failure_if_unconfirmed` uses one atomic conditional SQLite upsert to preserve prior DOWNLOADED history.
- If publication succeeds but SQLite save fails, keep final and stable Generate remote ID, block re-download because final is already present, and require explicit manual reconciliation. Never delete/overwrite the file or silently retry to "fix" the state.
- Race validation ran on GitHub's actual Windows runner using ThreadPoolExecutor, real paths and SQLite plus deterministic controlled provider fakes. Tests do **not** prove real Google account/Flow UI behavior.

## Gates / future
Official R03 CI https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37724196252: 165 tests, 30/30 frozen UI, Windows portable/smoke all PASS.
R04 combined regression, source-SHA/CI artifact audit remains NEXT, not automatically authorized.
Real-account login/restart gate and live Flow Generate/Download remain BLOCKED.
