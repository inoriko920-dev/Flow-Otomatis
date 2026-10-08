# E12-00 — GitHub documentation intake (partial)

Date: 2026-10-08 WIB. Scoped repository: inoriko920-dev/Flow-Otomatis.
Original baseline main: `e560684e04ed3a5fad40bb00a91823de68ca5431`.
Approval basis: user replied "lanjutkan" to the previous request to place V1.1 and E12-00 documentation into this repository, with no coding.

## Exact original artifacts pending GitHub binary upload
- `docs/planning/step12/MASTER_PLAN_FLOW_OTOMATIS_V1_1_IMPLEMENTATION_READY_2026-10-08.docx` — SHA256 `ace281206f8f7089643a51328486f6e949c706f1a9c8710fc5f500c664f04f71`, 79,528 bytes.
- `docs/planning/audits/E12_00_ASTRA_BASELINE_GOVERNANCE_FLOW_OTOMATIS_2026-10-08.docx` — SHA256 `9cc648b90a4c802558f6cea4435770396c926abcb6796897d958424e595ba05e`, 47,452 bytes.
- Master V1.0 archival original is in the user's separate planning ZIP and also should be retained for complete lineage (SHA256 `2b62e023f50a20da698ee8c47819d1e1246e7b8a6610bf6be27436bd5a02b70a`); existing repository has prior STEP 00-07 DOCX.

The original DOCX files were verified in the working container, but the connected GitHub action can submit UTF-8 text/base64 strings, not directly take a local sandbox file path. Binary upload has NOT been accomplished in this PR. The searchable extracted text below is supplementary only; it does not replace approved DOCX.

## Additional documented alternative (2026-10-08)
The user requested that the assistant try TXT, MD or other formats rather than require a manual DOCX upload. On this branch, two full-text TXT files and two newly **reconstructed** valid Office Open XML DOCX binary blobs were produced from the existing readable text mirror. The new binary files are distinguishably named *_RECONSTRUCTED_*. They are NOT byte-identical to the original 32-page / 6-page approved DOCX and do not preserve native table/image layouts. Original 79,528/47,452-byte DOCX and their hashes above remain pending if exact master archival fidelity is necessary.

- `docs/planning/step12/MASTER_PLAN_FLOW_OTOMATIS_V1_1_RECONSTRUCTED_2026-10-08.txt` and `.docx` — full extracted text of V1.1, 1,889 original extracted lines; reconstructed binary ZIP 181,209 bytes; Git blob `e09fc13e13c80b588cb46fd655ca7d19f01692de`.
- `docs/planning/audits/E12_00_ASTRA_BASELINE_GOVERNANCE_RECONSTRUCTED_2026-10-08.txt` and `.docx` — 380 extracted lines; 35,179-byte DOCX; Git blob `f965798f9901c93d602832a933e4a2569aff3530`.
- TXT and DOCX content reconstructed from text sources committed in this same review branch; no original DOCX layout is claimed, and E12-00 source-of-truth review is still required.

## Gate
- E12-00 T01-T04: reviewed/PASS based on earlier audit.
- E12-00 T05: PARTIAL — readable mirrors, full TXT and reconstructed DOCX in PR; exact original archival DOCX/owner acceptance and merge remain pending.
- G0 Docs Authority: BLOCKED. Do not begin E12-01 coding, UI changes, or Generate.
- Live Google Flow / multi-account policy, tariff/entitlement, REAL READY-after-restart: still BLOCKED or unverified; no provider calls.

## Next
After attaching exact DOCX binaries, verify their SHA-256 in GitHub, compare main/PR diff and CI, and only then update PROJECT_STATE.md and TASKS.md and request approval to merge. E12-01 is ASTRA planning only, not coding.

No source, schema, browser, UI, tokens or user credit should be changed by this branch.
