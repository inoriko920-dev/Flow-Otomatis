# SOURCE OF TRUTH MANIFEST — S08-T01

Status: **VERIFIED_IN_REPOSITORY**

Mandatory planning/reference DOCX files physically committed to the repository:

| Repo path | Bytes | SHA-256 | Status |
|---|---:|---|---|
| docs/planning/00_STEP_00_RISET_REPO_DAN_ARSITEKTUR_GOOGLE_FLOW_MANAGER.docx | 52737 | e75ec1e814bbb9e9d35dc3d342f631256b72bfdbf20260ef4a0ae9b2980bb3c9 | VERIFIED |
| docs/planning/00_STEP_00_PROJECT_INTAKE_FLOW_OTOMATIS_FACTORY_V2.docx | 51064 | 97b1176ca760284eab7559a659d44e64b5255e8fe8453edef1a11172bdd5e53d | VERIFIED |
| docs/planning/01_STEP_01_PRODUCT_DEFINITION_FLOW_OTOMATIS_FACTORY_V2.docx | 64573 | 83baea1b24865ee0a64b38044ed200bd320789c55d48dfcf9bb93281253d6132 | VERIFIED |
| docs/planning/02_STEP_02_EXISTING_SOLUTION_GITHUB_DISCOVERY_FLOW_OTOMATIS_FACTORY_V2.docx | 60215 | 3e027f10e3350123a19b829516802f6453661016db4bcf97722f52a4fb6d4eab | VERIFIED |
| docs/planning/03_STEP_03_UI_UX_INVENTORY_FLOW_OTOMATIS_FACTORY_V2.docx | 74759 | ef4f43675a9d85d511563abf00c00b7ff409924407578fa4e1220d7c2c990bee | VERIFIED |
| docs/planning/archive/04_STEP_04_UI_DESIGN_PROMPT_PACK_FLOW_OTOMATIS_FACTORY_V2_SUPERSEDED.docx | 62152 | d214e0fdbe009ae767ee0f3ab61d4226ec891eaeb7588d8824b826519f05e1e0 | VERIFIED |
| docs/planning/archive/04_STEP_04_UI_DESIGN_PROMPT_PACK_FLOW_OTOMATIS_FACTORY_V2_REV_FLOW_LOCK_V1_1_SUPERSEDED.docx | 64206 | 4ca87a414a4d15e5d5f9cfae5d5f444b8d1aa8ae4500be5d40bc63a832fb86bf | VERIFIED |
| docs/ui/04_STEP_04_UI_DESIGN_PROMPT_PACK_FLOW_OTOMATIS_FACTORY_V2_BIOGRAPHY_SYNC_V1_2.docx | 67813 | 53f1ef67cedc99a3405d9519506648564f7aa9291e27b3c9189c4078ea907d11 | VERIFIED |
| docs/ui/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx | 329255 | fa0ece85486dc8f9b011c947b7c3ae396ac20e37a23b75ec577fc9970912fa52 | VERIFIED |
| docs/planning/05_STEP_05_UI_FREEZE_PRODUCT_BLUEPRINT_FLOW_OTOMATIS_FACTORY_V2.docx | 64701 | 899d5b80608cd920044da9faab9be867c7ee365cf25e3e9847a970615eff86a3 | VERIFIED |
| docs/planning/06_STEP_06_ARCHITECTURE_TECHNOLOGY_DECISION_FLOW_OTOMATIS_FACTORY_V2.docx | 67916 | 58e417e7241c74260ed2b4ca317bdb8b4b3d5fb0505772c400ee1ef9736be5e5 | VERIFIED |
| docs/planning/07_STEP_07_CODE_CONSTITUTION_REPOSITORY_ARCHITECTURE_FLOW_OTOMATIS_FACTORY_V2.docx | 62314 | ded551edca9e557aff637d7989bc3c2adf2d5bae6ef14593304138190b2bdb4b | VERIFIED |
| docs/planning/FLOW_OTOMATIS_SYNC_REVISION_SPEC_FOR_100_FAMOUS_PEOPLE.docx | 61194 | b3c6c416c91fee917e693faadfce3eb4fde72d872798d77ebdbed5e263134956 | VERIFIED |

## STEP 12 audit remediation source of truth
The ASTRA audit handed to SOL on 7 October 2026 is represented in the repository at:
- `docs/planning/audits/00_ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-07.docx`
- original uploaded source: 48486 bytes, SHA-256 `1011693e1e67673a4af49378ca2009e93f596a74f563276ae060ebcaae0ca210`
- repository DOCX: compact text-equivalent copy, 10028 bytes, SHA-256 `39ee9d8c37aa573f019649b7f6f04c76812e80cf88b397e5694e0c96f9946527`
- integrity note: the repository copy preserves the complete logical audit text in document order; layout/tables are simplified because the connector truncated the first binary-identical upload attempt. The compact DOCX was reopened and rendered successfully to five pages before commit.
- audit baseline: `e6724a0a5c3d68789149ed5c7eb094d44c9f0967`
- implementation packages: A00–A05 inside STEP 12
- live Generate gate remains BLOCKED until the existing real-account restart validation passes.

The audit does not supersede the STEP 00–07 planning or the frozen UI reference. It is an implementation-remediation plan for the current STEP 12 baseline.

## Software Factory
Complete TXT guidance from the Software Factory V2 package is mirrored at:
- `docs/software_factory/SOFTWARE_FACTORY_V2_TEXT_GUIDE.md`

## UI reference rule
All 30 approved UI compositions are consolidated into:
- `docs/ui/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx`

The repository copy is image-compressed for repository efficiency while preserving all 30 compositions, final STEP 04 decisions, and implementation overrides.

## Superseded documents
Earlier STEP 04 planning versions are retained under `docs/planning/archive/` and are not active source-of-truth.

## Gate
S08-T01 remains PASS. The STEP 12 audit remediation track has its own A00–A05 gates and does not reopen S08-T01.
