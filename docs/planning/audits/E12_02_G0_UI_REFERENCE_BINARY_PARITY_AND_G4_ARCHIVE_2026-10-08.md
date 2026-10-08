# Flow-Otomatis — E12-02 post-approval asset archive and G0 UI authority parity audit

**Date:** 2026-10-08 WIB  
**Scope:** read-only verification + planning evidence. No app code, merge or live Google Flow actions.

## A. E12-02: owner-approved assets and outstanding archive

The owner explicitly approved all **22 exact V2 mockups**, including illustration/sample-data differences. The final DOCX was created with those PNG bytes preserved (22/22 exact), verified as 27 pages.

| Artifact | Bytes | SHA-256 | GitHub state |
|---|---:|---|---|
| FINAL approved 22-UI DOCX | 29,674,786 | `9a84372cbb10ad5e2db2d070c1d20319759aabee11ff85324a1193544ec6f1dd` | **NOT YET UPLOADED as binary** |
| FINAL 22-PNG + DOCX ZIP | 59,446,892 | `ad6f7a49efeee690384f3e1126d5d546bec81b21e7203d4e53c2c0fece8fc6da` | **NOT YET UPLOADED as binary** |

In-container recheck: both filenames and SHA-256 match prior approved manifest; final ZIP contains **27 entries**, CRC **PASS**. 22 image hashes per `docs/ui/final/E12_02_APPROVED_22_UI_MANIFEST_AND_HANDOFF_2026-10-08.md`.

**Transfer limitation:** the available GitHub connector supports creating text documents and creating Git blob objects only when given complete content; no authenticated bridge to feed local ~59 MB binary data into those parameters is available in this session. Direct GitHub remote transfer from the container is unavailable. **Do not fabricate a binary upload, success status or matching Git blob.**

### Required GitHub archival step

Under the approved UI review branch (or a new dedicated review branch; **never directly alter `main`**):
1. Upload **unchanged bytes** of all 22 PNG into `docs/ui/final/assets/`, and the FINAL DOCX into `docs/ui/final/`.
2. Verify all 22 PNG exact SHA-256 values plus the FINAL DOCX exact SHA-256 against the approved manifest (not just names or visual resemblance).
3. Confirm one-to-one 22 IDs, no replaced artwork, original 30 UI references unchanged, only docs/images added, CI branch review PASS.
4. Record actual commit ID and uploaded Git blob SHA/size evidence; do not claim G4 archival PASS until independently checked.
5. Preserve PR #25 as **draft/unmerged** until final review; no app code.

## B. G0 original 30-image reference authority — newly measured binary facts

Main-branch `docs/ui/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx`:
- GitHub API recursive main tree reports **329,255 bytes**, Git blob SHA-1 **`6e93a7e654e84ba2dd37af1fbc31c68ce3107f26`**.
- `docs/ui/UI_REFERENCE_MANIFEST.md` explicitly labels this as a **compressed-image DOCX** created to keep repository size practical; so its smaller size is **not automatically a file corruption bug**.
- Local original reference DOCX, available in project handoff: **41,006,814 bytes**, SHA-256 **`1549d0c9d39d71632abfab15f454fa291a7cdd5c6253453432f87fc5fd57711f`**, computed Git blob SHA-1 **`88b08c8c2ef001fc7d22aecd04625a75c206064d`**.
- Local original ZIP/DOCX integrity PASS; **30 images embedded**, about **46,192,516 bytes uncompressed** across `word/media/`.

**Firm conclusion**: the GitHub `main` DOCX is **not byte-identical** to the 41MB local original (Git SHA and byte size differ). **No conclusion about pixel/visual parity is justified from sizes alone.** The remote compressed DOCX's images were **not extracted and compared** in this audit. The compressed variant **may** serve as adequate UI reference if separately tested and approved, but this has **not been established** for strict G0.

### Resolve G0 without overwriting authority

Option 1 (preferred if preservation is mandatory): archive the **exact original 41,006,814-byte DOCX** under a distinct provenance path, not by overwriting the existing 329,255-byte compressed DOCX; verify exact SHA-256 and Git blob SHA-1.

Option 2 (owner-approved exception only): compare all 30 compositions' text/layout/crop and images from original and compressed reference, document substantive equivalence/differences, and obtain explicit approval of the compressed surrogate as design authority. This does **not** mean byte-identical preservation.

Both options require a binary-capable authenticated transfer or retrieval capability not currently present in the connector channel. Do not auto-approve either.

## C. Gate decisions as of this audit

| Gate | Status | Proof/remaining work |
|---|---|---|
| E12-02 22/22 visual signoff | **PASS** | Owner expressly approved exact V2 images |
| E12-02 single FINAL DOCX | **PASS locally** | 27 pages; 22/22 original PNG embedded |
| E12-02 GitHub binary archive | **PENDING** | Approved PNG/DOCX not committed |
| **G4 overall** | **NOT YET PASS** | Pending GitHub binary evidence |
| **G0 strict** | **BLOCKED** | Original 30-image DOCX vs intentionally compressed GitHub variant not byte-identical; authority parity not established |
| G1 provider multi-account permission | UNKNOWN / BLOCKED | Real terms and eligibility evidence required |
| G5 tariff/credit snapshot | UNKNOWN / BLOCKED | Real allowed pricing and per-account verifiable credit evidence |
| G6 READY after restart | UNVERIFIED | Live session evidence, no bypass |
| ADR-020–023 ASTRA T06 | PROPOSED / PENDING | Required explicit architecture decision and tests |

**STOP:** no `src/` or executable code changes, migrations, PR merge, real browser automation, multi-account credit use, Google Flow Generate or Download until gates are demonstrably PASS. Approval of UI images does **not** authorize software implementation.
