# SOL F01–F05 — ASTRA audit bugfix handoff, 10 October 2026

## Source of truth
- User-supplied ASTRA DOCX and TXT dated 2026-10-10. This document is an implementation handoff rather than the original audit.
- Repo `inoriko920-dev/Flow-Otomatis`, Draft PR #34, original audited head `48d5fda77a63e8bda06016232e51ecabd9a98bf1`.
- Scope locked to F01–F05. No live Google Flow Generate/Download, no credits, no new features, no UI/logo changes. No merge without all required gates.

## Code ownership and outcomes
| Finding | Changed canonical ownership | Verified behavior / acceptance |
| --- | --- | --- |
| F01 | `contracts/package/import_manifest.py`; `infrastructure/persistence/sqlite_workspace_repository.py` | Reject timezone-naive dates before mkdir/write; keep Z, positive and negative offsets; no auto-repair corrupted legacy DB. |
| F02 | `application/services/local_generation_queue.py`; `workers/browser/google_flow_generation.py` | Allowlisted fixed error messages for all Generate failures; never store raw exception/driver detail; preserve attention categories. |
| F05 | `infrastructure/persistence/sqlite_generation_job_repository.py` | Read-only SQLite job list, legacy decode, future version rejection and rollback-on-failed explicit migration. |
| F03 | `application/services/local_results.py`; `infrastructure/persistence/sqlite_download_result_repository.py` | Verify current Scene fields against immutable job snapshot; cached MP4 read and atomic Download save must not approve stale revisions. Preserve old MP4/history. |
| F04 | `application/ports/generation_provider.py` and `__init__.py`; `workers/browser/google_flow_generation.py`; `application/services/local_generation_queue.py` | Typed proven-safe failure, explicit reprepare only; unknown/contradictory evidence and ACCEPTED without ID stay ambiguous. |

## Regression ownership
- F01: `tests/integration/test_episode_import_slice.py`; old-project isolation in `test_project_library_wave.py`.
- F02/F04: `tests/integration/test_local_generation_queue_wave.py`; `test_google_flow_generation_contract.py`.
- F05: `tests/integration/test_generation_repository_readonly.py`; explicit old-schema migration in queue-wave tests.
- F03: `tests/integration/test_local_results_wave.py` and `test_generated_media_download_foundation.py` with realistic matching Scene fixture.

## Verification and status
- Quality evidence: 702 passing tests, Ruff format/lint PASS, mypy 91 source modules PASS, architecture PASS at `8d44a43b511cac1784c26d7f8164fa3ac971c2f4`; see https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/38048442995.
- Cache-reuse revision guard was added later at `a34e8de58470b98bacdaadfec8a910f7c8a353e3`. **Do not mark all gates PASS on this code until latest CI for head completes.**
- Windows CI must independently pass `quality`, `offline-simulator-windows`, `ui-visual`, `uix22-qt-windows`, and `package-windows` on final SHA.
- Draft PR #34 remains unmerged; live Flow / production-account and G0 E12 gates independently blocked.
