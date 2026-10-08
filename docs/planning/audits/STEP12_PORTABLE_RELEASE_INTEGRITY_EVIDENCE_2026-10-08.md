# STEP 12 — Additional Portable Release Integrity QA
**Date:** 8 October 2026 WIB
**Scope:** `inoriko920-dev/Flow-Otomatis` • only portable distribution/CI.
**Gate:** **PASS** for packaged Windows release verification; this does not certify live Flow.

## Delivered
- [PR #18](https://github.com/inoriko920-dev/Flow-Otomatis/pull/18) merged as `baff19bb7c28612837d24001b9db9ee4a84251e5`.
- `scripts/verify_portable_artifact.py`: reads distributable ZIP, compares its bytes to `SHA256SUMS.txt`, checks archive CRC, expected Git source SHA and credential-free `BUILD_MANIFEST.json`; rejects unsafe ZIP paths, Windows reserved names, duplicate casefold names, symlinks, encrypted entries, missing EXE/Chromium and missing dependency notices.
- `scripts/build_portable.py` now regenerates `THIRD_PARTY_NOTICES.txt` **after** cleaning `dist/`, requires nonempty output, and includes it in the built bundle/ZIP. The previous pre-build CI step generated the notice too early; `build()` removed it during clean. The actual ZIP check revealed this real distribution error.
- `.github/workflows/ci.yml` verifies the ZIP **after** bundled EXE smoke and **before** artifact upload. A failing integrity gate prevents publishing a purportedly verified artifact.
- `tests/contract/test_portable_artifact_integrity.py` and `tests/unit/test_portable_build_notices.py`: positive ZIP verification, tampering/CRC and checksum cases, path safety, wrong SHA/live claims, incomplete bundle, regenerated notices following cleanup and fail-closed missing inventory. No production UI or Flow live changed.

## Official Windows proof on merged main
- **Exact tested source SHA:** `baff19bb7c28612837d24001b9db9ee4a84251e5`.
- **Official full main CI:** https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/37728080637 — SUCCESS, all three jobs.
- Quality job `113150698266`: Python 3.14.7 + frozen uv; Ruff format/lint, mypy 81 files, architecture PASS; **217 pytest passed**.
- Frozen UI job `113150984880`: **30/30 PASS**.
- Windows job `113151228484`: staged Chromium and Chromium smoke, portable PyInstaller onedir ZIP, portable EXE smoke and new ZIP integrity validation: **PASS**.
- Real distribution ZIP: **1,049 members**, internal ZIP SHA-256 `b58bba7b18517f67e6db5a79b299f3bd170a20c5536ab8f11c7d9ed4bfc3a6b2`; manifest source `baff19bb7c28612837d24001b9db9ee4a84251e5`.
- Official artifact `11528593129`, name `Flow-Otomatis-step12-i12-01-restart-proof-win-x64`, upload-wrapper size **435,725,381 bytes**, wrapper SHA-256 `17e9c36b2f6db95f99ba5fb9fa3a0e4234dd5c188191c12f625cb1cd105a9431`, expires **2026-10-22T04:38:25Z**.
- UI evidence artifact `11528304019`, size **3,316,911 bytes**, wrapper SHA-256 `64d26a26334e38249fb0b78862f6bd3d2cfd6d667a5d1dc7016ffc84a2793c8e`, expires **2026-10-22T04:35:48Z**.
- Artifact wrapper SHA-256 and *inner distributable ZIP* SHA-256 describe **different files**; never substitute one for the other.

## Remaining separate gates
- User reports manual Google login can work; **no evidence of same-profile READY surviving a full app restart was submitted in this chat**.
- I12-01 real account restart proof: **PENDING / NOT independently verified**.
- Live Google Flow one-Scene Generate (I12-02B2-LIVE) and result Download (I12-03-LIVE): **BLOCKED, NOT TESTED**.
- B01–B06 offline ASTRA audit R00–R04 remains COMPLETE/PASS and unchanged; no fresh live provider claims.
- Artifact CI files expire; this release QA is not a durable off-GitHub source backup.
