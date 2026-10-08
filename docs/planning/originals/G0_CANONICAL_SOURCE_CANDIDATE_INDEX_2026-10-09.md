# G0 — Original DOCX authority candidate index (REVIEW, no owner signoff)

**Verified 2026-10-09 WIB.** This is a safe navigation/index entry on **Draft PR #27**, not a change to any original source, not a final canonical authority decision, and not approval for implementation. Read with `docs/planning/SOURCE_OF_TRUTH_MANIFEST.md`, `PROJECT_STATE.md`, `docs/ui/IMPLEMENTATION_OVERRIDES.md`, and active `AGENTS.md`.

## What is physically available — all original candidate binaries verified on GitHub

| Stage / purpose | Existing exact binary in this branch | Evidence and proposed review use | Decision state |
|---|---|---|---|
| E12-00 baseline/source snapshot (15:20) | `docs/planning/originals/2026-10-08/E12_00_ASTRA_BASELINE_GOVERNANCE_1520_WIB_SOURCE_2026-10-08.docx` | Earlier original candidate, SHA-256 `2df71a84b3f33ba3e04114f0508764d9de7d798fa6926b1aa5dfbfbd7f0f5452`; preserve for traceability. | Preserved, not independently signed off. |
| E12-00 baseline/handoff (15:21) | `docs/planning/originals/2026-10-08/E12_00_ASTRA_BASELINE_GOVERNANCE_1521_WIB_HANDOFF_2026-10-08.docx` | One-minute-later handoff, SHA-256 `9cc648b90a4c802558f6cea4435770396c926abcb6796897d958424e595ba05e`; **recommended active E12-00 candidate** solely on date/handoff ordering; 279/279 text runs differ only in 15:20 versus 15:21 timestamp. | Recommended; owner must confirm authority. |
| E12 Master Plan V1.1 | `docs/planning/originals/2026-10-08/MASTER_PLAN_FLOW_OTOMATIS_V1_1_IMPLEMENTATION_READY_2026-10-08.docx` | **Recommended primary V1.1 original Word source**, SHA-256 `ace281206f8f7089643a51328486f6e949c706f1a9c8710fc5f500c664f04f71`; 705 nonempty paragraphs and 42 tables; original ends **"MENUNGGU PERSETUJUAN SEBELUM GITHUB/CODING"**. Do not substitute reconstructed Word. | Original confirmed; final plan approval PENDING. |
| E12-01 ADR draft | `docs/planning/originals/2026-10-08/E12_01_ASTRA_ARCHITECTURE_ADR_FLOW_OTOMATIS_2026-10-08.docx` | Initial original (107 text paragraphs, 11 tables), SHA-256 `9b3dd7cc9758f135c66541effa878b56a708c9b272d6698a4b92b2d585efc74d`. Keep as historical review input. | Preserved historical, not authoritative. |
| E12-01 ADR V1.1 review | `docs/planning/originals/2026-10-08/E12_01_ASTRA_ARCHITECTURE_ADR_V1_1_GITHUB_REVIEW_2026-10-08.docx` | **Recommended current ADR review candidate**, SHA-256 `0eab21d9664a31d187bb6c168ae47766462ed896e494b95021d10874855d58a3`; 129 nonempty paragraphs and 17 tables; compare live `docs/architecture/ADR-020..023` and separate Draft PR #26 errata. The DOCX explicitly marks ADRs **PROPOSED / T06 PENDING**. | Review candidate, not an approved architecture. |
| E12-02 design prompt specification | `docs/planning/originals/2026-10-08/E12_02_ASTRA_UI_PROMPT_PACK_22_GAMBAR_2026-10-08.docx` | Original 9-group/22-prompt design planning package, SHA-256 `b8224da4460bb66df3cebba15fc1a4bbdb49c2a293ac80396b2eddbc720fa8ec`; **historical prompt**, not visual authority after 22 designs were approved. | Preserved historical; images approved via PR #25. |

All **6/6 exact Git blobs and byte sizes PASS** at PR #27 real Windows upload commit `3a5fba85114a3f8d22ba4ceda9983de0a6ed3b1a`. Post-upload audit `docs/planning/audits/G0_2026_10_09_REMOTE_SIX_DOCX_VERIFIED_AND_AUTHORITY_PENDING.md`. No repeat upload required.

## Frozen UI source-of-truth — do not inadvertently replace approved images

- **30 existing previously approved UI designs**: highest-fidelity candidate is the **original uncompressed Word** at **PR #25** `docs/ui/original_uncompressed/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx` (SHA-256 `1549d0c9d39d71632abfab15f454fa291a7cdd5c6253453432f87fc5fd57711f`, 30 original PNG images). **Recommend treating original as visual authority**, conditional on explicit owner/ASTRA decision, while preserving the distinct `docs/ui/IMPLEMENTATION_OVERRIDES.md`.
- Older `main` reference `docs/ui/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx` is an **intentional JPEG-compressed working copy**, size 329,255 bytes and 30 JPEG. It is **not byte/structurally equivalent** to the original; 4 of its 17 non-media ZIP members differ (including `word/document.xml`). Treat it as a **convenience/historical reference candidate only** until authority and visual parity are explicitly decided, **not** as a proven identical substitute.
- **22 new owner-approved E12-02 UI designs** are preserved at **PR #25** `docs/ui/final/assets/` (22 PNG) and `docs/ui/final/FLOW_OTOMATIS_E12_02_REFERENSI_UI_FINAL_22_DESAIN_DISETUJUI_2026-10-08.docx`, approved exact 27-page reference. Their **24/24** Git blob SHA and sizes verified; **G4 archive PASS**. New UI addenda supplement, do not silently rewrite, the 30 frozen originals.
- Both PR #25 and PR #27 are currently **DRAFT and unmerged**. Draft branch files must not be claimed to reside on `main`. Do not merge or update code without the required approval.

## Required G0 authority choices before source/implementation gate may be PASS

**Decision G0-A** — For the original 30 frozen UI images, approve `docs/ui/original_uncompressed/...` as canonical visual reference, and classify the old compressed JPG DOCX as a preview/historical copy only; if selecting compressed instead, require formal page-by-page visual and textual parity proof.

**Decision G0-B** — For E12-00 source, select either 15:21 WIB handoff as authoritative with 15:20 archived for provenance (recommended), or explain another audited source choice. The difference in Word text runs is timestamp only, **not competing policy decisions**.

**Decision G0-C** — Identify original Master Plan V1.1 as source of planning review and original E12-01 ADR V1.1 as current review draft; leave architecture statuses and Master Plan approval **PENDING** until explicit owner/ASTRA signoff. Separate reference precedence from actual authorization to code.

**Gate outcomes after archival**: G0 physical DOCX preservation **PASS (6/6)**; G4 visual/asset archival **PASS (24/24)**; G0 **overall PENDING owner authority decisions**; T06 **PENDING**, G1 multi-account automation permission **UNKNOWN**, G5 live account tariffs/credits **UNVERIFIED**, G6 READY-after-restart **UNVERIFIED**. No live Google Flow, credit use, migration, application coding or automatic merge.

## Safe progression

1. Owner reviews G0-A/B/C recommendations without editing the original files. Request one clear explicit approval of authority selection.
2. Update source-of-truth links and gate decision history **on review branches only**, then verify separate G1/G5/G6/T06 requirements. Any real app implementation must wait for all relevant gates.
3. Use original E12-01 V1.1 and updated ADRs from PR #26 to prepare/approve T06 (not inferred from `lanjutkan`).
