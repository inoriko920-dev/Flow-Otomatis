# Flow-Otomatis — E12-02 approved UI GitHub upload kit prepared (NOT YET PUSHED)

**Date:** 2026-10-08 WIB. **Owner authorization:** explicitly approved all exact 22 V2 UI images and requested GitHub archiving; prohibited starting code until ALL gates PASS. Scope of this handoff: archival only.

## Prepared one-package upload kit (conversation artifact, NOT a GitHub file)

Filename: `FLOW_OTOMATIS_E12_02_PR25_ARSIP_SIAP_UNGGAH_2026-10-08.zip`  
Size: **100,450,016 bytes**  
SHA-256: **`df0593d23792af1f17ddfa420032e469be0ad1775585c78311ddaf4bb0ea5860`**  
ZIP CRC: **PASS**; 30 entries. Largest member 41,006,814 bytes (under GitHub's 100-MB per-file limit).

### Exactly 24 binary artifacts

1. All **22 explicitly approved UIX-01-A .. UIX-09-B PNG**, unaltered 1920×1080 files from the approved ZIP, matching the 22 SHA-256 hashes recorded in `docs/ui/final/E12_02_APPROVED_22_UI_MANIFEST_AND_HANDOFF_2026-10-08.md`.
2. Exact **FINAL 27-page UI reference DOCX**: 29,674,786 bytes, SHA-256 `9a84372cbb10ad5e2db2d070c1d20319759aabee11ff85324a1193544ec6f1dd`. The 22 PNG embedded in DOCX were independently compared byte-for-byte to source files.
3. Exact **original 30-image G0 reference DOCX**: 41,006,814 bytes, SHA-256 `1549d0c9d39d71632abfab15f454fa291a7cdd5c6253453432f87fc5fd57711f`. This is stored under a **new** provenance folder: do not overwrite the 329,255-byte compressed UI reference already on main.

The package also contains `PAYLOAD/MANIFEST_PR25.json`, `PAYLOAD/SHA256_PR25.txt`, `BACA_DULU.txt`, `CEK_SAJA.cmd`, `UPLOAD_PR25.cmd` and `UPLOAD_PR25.ps1` (script SHA256 `b9f5fb9ce4510be72d6e1d3acb678478c461cf7a25dfcd44c7f567f5fb2bfd12`).

### Target GitHub locations, all on PR #25 review branch ONLY

- 22 PNG -> `docs/ui/final/assets/<unchanged original filename>.png`
- Final DOCX -> `docs/ui/final/FLOW_OTOMATIS_E12_02_REFERENSI_UI_FINAL_22_DESAIN_DISETUJUI_2026-10-08.docx`
- Original G0 DOCX -> `docs/ui/original_uncompressed/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx`
- Manifest -> `docs/ui/final/E12_02_APPROVED_BINARY_ARCHIVE_MANIFEST.json`.

Archive preparation validation:
- All 24 binaries SHA-256/size check **PASS**; 22 PNG IHDR dimensions 1920×1080; final DOCX 22 media images match approved PNGs; original Word ZIP CRC PASS.
- **Local Git staging simulation PASS**: 25 tracked paths (22 PNG + two DOCX + one JSON), all in allowed `docs/ui/**` paths, no source-code paths.
- Two Windows helpers are supplied: `CEK_SAJA.cmd` runs local verification only; `UPLOAD_PR25.cmd` verifies before cloning/pushing to existing `docs/e12-02-uix-prompt-only-20261008`, checks remote URL and clean checkout, rejects existing different hashes, stages only listed paths, pushes branch, verifies remote SHA. Does **NOT** merge.
- Windows PowerShell runtime with Git authentication/push **NOT TESTED** in this container. The GitHub remote is unreachable from the local file container (DNS failure), and no supported connector accepts a local binary file path as blob input.
- This documentation PR update is **NOT** evidence the upload was done. **Zero new image/DOCX binaries have been committed to PR #25 so far.**

## Next gated step

Obtain an authenticated binary-capable GitHub environment (e.g. execute the included uploader under the owner's approved Git for Windows credential, or use a permitted cloud-computer upload session). Push ONLY to the review branch, then independently re-read GitHub Git tree and exact binary SHA-256. Report the real commit SHA. Until then: **E12-02 visual signoff PASS**, **G4 binary archive PENDING**, **strict G0 BLOCKED**, **G1/G5/G6/ADR T06 PENDING**. No merge, app code, browser automation or credit use.

Even after the original 30-image DOCX is archived, **strict G0 may remain blocked** for other original planning DOCX authority and full parity evidence; do not auto-close G0 merely because this kit includes that Word file.
