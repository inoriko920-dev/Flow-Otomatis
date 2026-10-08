# ADR-018 — STEP 12 B01–B06 Remediation Contracts
Date: 8 October 2026 WIB
Status: ACCEPTED FOR R01–R03 PLANNING, NOT IMPLEMENTED
Source: ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-08.docx.
Baseline: `0b9e2c4f63a9c0fdab0fe255830964a0e2fb6b39`.

## Existing owners and invariants
Extend existing canonical application service/ports, persistence, filesystem and Qt callback owners. Do not add a parallel state manager or service graph. Preserve ADR-015/016/017, STEP 04 frozen UI, per-project evidence, and Windows 11 portable contract. Production files and migrations are outside R00.

### B01 — Gemini health and selection
- Introduce a field-limited `update_health` repository operation: UPDATE existing key only (health status, checked time, sanitized detail); no INSERT/upsert, no mutation of is_active/label/fingerprint/masked_key.
- Keep manual `set_active` as sole selection operation. An older same-key completion must not override newer evidence; use in-flight single-key exclusion or monotonic request revision and verify with deterministic tests.
- No automatic key rotation, no raw-key persistence in SQLite.

### B02 — Qt Agent completion rights
- Request identity includes immutable request_id, episode_id, scene_id and context generation.
- Both success/error completion carry this identity. Only the matching active request for the currently displayed workspace can update answer or busy state.
- Scene/project/context change and window close invalidate old completions without claiming the network call can always be cancelled.
- Qt object lifetime and out-of-order response tests are mandatory.

### B03 — Verify image bytes before Generate
- Extend canonical EpisodePackagePort/package reader or a focused filesystem verification adapter behind an application port; correctly handle directories and ZIP entry lookup using `source_package_path`, never CWD.
- Prepare binds image identity to content digest or an immutable owned snapshot. Dispatch re-verifies actual bytes and rejects missing/unreadable/modified inputs before `mark_submit_started`.
- Persisted legacy queued revisions without valid content evidence may not be submitted. If adding persisted revision/digest columns, require an explicit transactional schema migration under ADR-016, preserving old jobs/remote_result_id/history.
- Never silently re-map image, duration or prompt; no ambiguous automatic retry.

### B04 — Effective video availability is not download history
- At snapshot and independently just before JSON export, check each recorded output is readable, nonempty regular file.
- Historical DownloadRecord remains immutable evidence; an unavailable output becomes an effective `UNAVAILABLE` state, lowers effective downloaded_count and blocks handoff.
- Manifest compatibility: v1.0 readers must not interpret an unavailable file as `DOWNLOADED`. R03 must add contract tests and document whether version bump or additive fields are needed before shipping. Do not write fake success to older schema.
- No silent redownload/regeneration, no deletion of historic Generate identity.

### B05 — Atomic no-clobber publication
- Replace `os.replace` with proven atomic Windows no-overwrite publish/claim primitive, plus a uniquely owned partial/attempt identifier.
- No overwrite even if destination appears while driver runs; competing attempts cannot share a partial. Cleanup only own attempt's partial.
- Keep conflicting destination and evidence for inspection; no arbitrary renaming/take changes or automatic Generate/retry.
- Publication-success/storage-failure recovery must be explicit and tested on Windows. Unsupported platform primitive must fail safely.

### B06 — Timezone-aware boundary
- Decode `created_at` and `imported_at` as strictly timezone-aware. Treat missing tzinfo or empty/invalid string as `WorkspaceCorruptError` on that project only.
- `scan_recent` continues listing valid projects, ordering by correct absolute chronology. Never assume local timezone or repair/source-write during read.
- If a historically documented valid legacy format used naive timestamps, stop R02 and re-review with ASTRA before migration.

## Review gates
R01 T01–T08 → R02 T09–T13/T22–T25 → R03 T14–T21 → R04 combined.
Original ASTRA harness code was not provided with the uploaded DOCX. Static source confirmation alone cannot close any bug.
No Flow live selector/login/Generate/Download or frozen UI redesign is authorized.
