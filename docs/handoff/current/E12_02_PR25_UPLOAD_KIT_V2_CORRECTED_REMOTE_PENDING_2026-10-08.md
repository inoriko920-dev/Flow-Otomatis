# E12-02 — PR #25 binary archival kit V2 (CORRECTED; NOT PUSHED)

**Date:** 2026-10-08 WIB | Scope: approved UI assets only | PR: #25 **DRAFT** | No app code / no merge.

## Critical fix to preceding V1 kit

The preceding `FLOW_OTOMATIS_E12_02_PR25_ARSIP_SIAP_UNGGAH_2026-10-08.zip` contained a PowerShell **`RunGit` positional argument bug**: invocations like `RunGit @('clone', ...)` did not explicitly bind the complete array to the `[string[]] $Arguments` parameter. Treat V1 as **SUPERSEDED — DO NOT USE**.

A corrected ZIP (available as a downloadable ChatGPT artifact) has now been assembled:

- **Use this:** `FLOW_OTOMATIS_E12_02_PR25_ARSIP_SIAP_UNGGAH_V2_DIVERIFIKASI_2026-10-08.zip`
- **Bytes:** 100,355,921
- **SHA-256:** `e51789935bc414e62597403e19a0871d21af65612e06f1fecc581216d9a87c09`
- Embedded `UPLOAD_PR25.ps1` SHA-256: `f116c601c091dd1bd501cc26a5e6bf9a17f19457d01ac01022b09f6ee12389a2`
- Corrected explicit calls `RunGit -Arguments @( ... )` for clone, add, commit and push.
- Hardened destination: exact 22 PNG path pattern, exact final DOCX path and original G0 DOCX path; manifest target exactly `docs/ui/final/E12_02_APPROVED_BINARY_ARCHIVE_MANIFEST.json`.
- Post-push checks: local committed Git blob hashes compared with hashes of the 24 input binaries; remote HEAD must equal the locally verified commit HEAD.

## Immutable approved binary data

Exactly **22 V2 PNG + one final 27-page DOCX + one original 30-reference G0 DOCX**, **24/24 unchanged** from owner approved inputs (same prior manifest SHA-256). V2 ZIP CRC **PASS**, 30 archive entries.

- Exact final DOCX SHA-256 `9a84372cbb10ad5e2db2d070c1d20319759aabee11ff85324a1193544ec6f1dd`.
- Original 30-reference G0 DOCX SHA-256 `1549d0c9d39d71632abfab15f454fa291a7cdd5c6253453432f87fc5fd57711f`, stores original under **new path**, does not replace compressed main reference.
- Images' exact hashes in `docs/ui/final/E12_02_APPROVED_22_UI_MANIFEST_AND_HANDOFF_2026-10-08.md`.

## Tests actually performed

- ZIP CRC + 24/24 embedded SHA-256: **PASS**.
- Script checks: five explicit `RunGit -Arguments @( ... )` call sites; destination and manifest path guards: **PASS static review**.
- **Local isolated Git rehearsal**: 25/25 staged paths under `docs/ui/`, 24/24 `git hash-object` / `git rev-parse HEAD:path` binary content comparisons PASS; no non-docs files.
- **PowerShell Windows runtime test**: **NOT RUN** (PowerShell unavailable in test environment). Thus real-world execution is not guaranteed; operator must review and test.
- **Real remote GitHub push**: **NOT DONE**; local environment could not resolve github.com. No GitHub binary upload claim permitted.

## Required action / STOP

On a Windows 11 machine with Git for Windows and authenticated GitHub push access, download and extract **only V2**, run `CEK_SAJA.cmd` then `UPLOAD_PR25.cmd`. Review console output; do not claim complete without PASS and a real remote HEAD commit.

After GitHub branch gains the binaries, independently verify all 24 exact image/DOCX Git blob hashes and SHA-256 by downloading/reading source bytes, record PR commit; only then may archival portion of G4 be marked PASS. Original 30-reference G0 parity and separate G0 planning source issues, G1 provider terms, G5 credit tariff, G6 session READY and E12-01 ADR-T06 remain independently blocked/unverified.

**DO NOT** merge, change app code, spend credits, use multi-account automation or claim gate closure until all controls PASS.
