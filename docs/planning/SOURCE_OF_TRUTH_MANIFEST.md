# SOURCE OF TRUTH MANIFEST — S08-T01

Status: **PENDING_BINARY_UPLOAD**

This manifest is authoritative for the binary source-of-truth gate. Production code under `src/` is forbidden until every REQUIRED entry below exists in the repository at the stated path and its SHA-256 matches.

## Required planning / reference binaries

| Repo path | Bytes | SHA-256 | Status |
|---|---:|---|---|
| docs/planning/SOFTWARE_FACTORY_ASTRA_SOL_COMPLETE_FINAL_V2.zip | 1196213 | 7e75836fd291b9794481dc33d1e711ce358d706bb0c9228aa7780747c85edcd9 | PENDING |
| docs/planning/00_STEP_00_PROJECT_INTAKE_FLOW_OTOMATIS_FACTORY_V2.docx | 51064 | 97b1176ca760284eab7559a659d44e64b5255e8fe8453edef1a11172bdd5e53d | PENDING |
| docs/planning/01_STEP_01_PRODUCT_DEFINITION_FLOW_OTOMATIS_FACTORY_V2.docx | 64573 | 83baea1b24865ee0a64b38044ed200bd320789c55d48dfcf9bb93281253d6132 | PENDING |
| docs/planning/02_STEP_02_EXISTING_SOLUTION_GITHUB_DISCOVERY_FLOW_OTOMATIS_FACTORY_V2.docx | 60215 | 3e027f10e3350123a19b829516802f6453661016db4bcf97722f52a4fb6d4eab | PENDING |
| docs/planning/03_STEP_03_UI_UX_INVENTORY_FLOW_OTOMATIS_FACTORY_V2.docx | 74759 | ef4f43675a9d85d511563abf00c00b7ff409924407578fa4e1220d7c2c990bee | PENDING |
| docs/ui/04_STEP_04_UI_DESIGN_PROMPT_PACK_FLOW_OTOMATIS_FACTORY_V2_BIOGRAPHY_SYNC_V1_2.docx | 67813 | 53f1ef67cedc99a3405d9519506648564f7aa9291e27b3c9189c4078ea907d11 | PENDING |
| docs/ui/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx | 41006814 | 1549d0c9d39d71632abfab15f454fa291a7cdd5c6253453432f87fc5fd57711f | PENDING |
| docs/planning/05_STEP_05_UI_FREEZE_PRODUCT_BLUEPRINT_FLOW_OTOMATIS_FACTORY_V2.docx | 64701 | 899d5b80608cd920044da9faab9be867c7ee365cf25e3e9847a970615eff86a3 | PENDING |
| docs/planning/06_STEP_06_ARCHITECTURE_TECHNOLOGY_DECISION_FLOW_OTOMATIS_FACTORY_V2.docx | 67916 | 58e417e7241c74260ed2b4ca317bdb8b4b3d5fb0505772c400ee1ef9736be5e5 | PENDING |
| docs/planning/07_STEP_07_CODE_CONSTITUTION_REPOSITORY_ARCHITECTURE_FLOW_OTOMATIS_FACTORY_V2.docx | 62314 | ded551edca9e557aff637d7989bc3c2adf2d5bae6ef14593304138190b2bdb4b | PENDING |
| docs/planning/FLOW_OTOMATIS_SYNC_REVISION_SPEC_FOR_100_FAMOUS_PEOPLE.docx | 61194 | b3c6c416c91fee917e693faadfce3eb4fde72d872798d77ebdbed5e263134956 | PENDING |
| docs/handoff/history/STEP_06_ARCHITECTURE_HANDOFF_FLOW_OTOMATIS.zip | 11842 | 81c7a94bd92213a640c5637fe72cdad88271b8422b6edcd6bee2c672d42e7879 | PENDING |
| docs/handoff/history/STEP_07_CODE_CONSTITUTION_HANDOFF_FLOW_OTOMATIS.zip | 12724 | 5064eb78c58abadd67abe07b2117db079d7c3e3b0ddf20eb6f70ff146ab16376 | PENDING |
| docs/ui/prompts/Flow-Otomatis_STEP04_UI_PROMPTS_SYNC_V1_2.zip | 93939 | 322fb1c632dafaf5e39360cecb152f9596986d925d0d4d816ce03cd696e5a4dd | PENDING |
| docs/ui/prompts/Flow-Otomatis_STEP04_UI_PROMPTS_SYNC_V1_2_BATCHED.zip | 18739 | 99f78377d93f3f3238c8ecb69d860cb58572c7c502415b7e17359d456c7ec3ef | PENDING |

The 30 final PNG files are separately listed in `docs/ui/UI_REFERENCE_MANIFEST.md`.

## Prepared repo-ready upload pack
A local repo-ready archive has been prepared with the exact canonical paths above plus all 30 UI PNG files:
- Name: `Flow-Otomatis_S08_T01_BINARY_SOURCE_OF_TRUTH_UPLOAD_PACK.zip`
- Size: 83847809 bytes
- SHA-256: `7f14ee5a877d041daa08a486628f8541d62fe1ecffdd20cd8b2230a28b56f107`
- ZIP integrity: PASS
- Entries: 47

The upload pack is a transfer aid only. S08-T01 remains PENDING until its contained files are actually present at their canonical repo paths.

## Gate rule
S08-T01 can be PASS only when:
1. every required binary entry is present at the canonical path;
2. every hash matches;
3. all 30 final UI PNG files in `docs/ui/UI_REFERENCE_MANIFEST.md` are present and hash-verified;
4. AGENTS/PROJECT_STATE/PLAN/TASKS and architecture/handoff text files are present;
5. repo contains no secrets/user session data/generated build data.

Until then: **NO PRODUCTION CODE**.
