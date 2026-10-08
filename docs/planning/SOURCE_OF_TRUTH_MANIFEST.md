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

## STEP 12 new 8 October audit — SOL R00 (B01–B06)
- Exact original ASTRA DOCX: `docs/planning/audits/ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-08.docx`.
- Original size: 48,799 bytes. SHA-256: `5481a09b85219615169c285d6bfd42bcc7398bcf881a73a604f2e7a351444fda`. Git blob: `0a7bd29f26e2f8b3bd489ba4e5b82cff47362fb4`.
- This upload is binary-identical to the user attachment; no simplification has been substituted.
- Source code reinspection: `docs/planning/audits/B01_B06_SOL_R00_CODE_EVIDENCE_2026-10-08.md`.
- Cross-module contract: `docs/architecture/ADR-018-step12-b01-b06-remediation-contracts.md`.
- Next AI handoff: `docs/handoff/current/HANDOFF_STEP_12_BUG_R00_TO_R01_2026-10-08.md`.
- The original, separate ASTRA Python/JSON reproducibility attachments were not provided. Not present.
- The STEP 00–07 docs, final UI 30-state authority, and 7 October audit A00–A05 remain intact.

## STEP 12 R03 B04/B05 closure (8 October 2026)
- Original planning authority remains `docs/planning/audits/ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-08.docx`.
- R03 evidence: `docs/planning/audits/B04_B05_R03_EVIDENCE_2026-10-08.md`.
- R03 ADR-019: `docs/architecture/ADR-019-step12-r03-results-availability-and-no-clobber.md`.
- Current handoff: `docs/handoff/current/HANDOFF_STEP_12_BUG_R03_TO_R04_2026-10-08.md`.
- CI tested `17dc2be0c7e4c69a99ab5129ea311492a182ecc4`, code merged `1f82675eb6282a3f5070c4320c5898a4304dd516`, 165 pytest/UI 30/Windows portable PASS.
- R04 combined verification not run. Historic F01–F06 and new B01–B06 locally closed, no Flow live claim.

## STEP 12 R04 final verified source-of-truth addendum (8 October 2026)
- ASTRA original unchanged: `docs/planning/audits/ASTRA_BUG_AUDIT_SOL_PLAN_FLOW_OTOMATIS_2026-10-08.docx`, SHA256 `5481a09b85219615169c285d6bfd42bcc7398bcf881a73a604f2e7a351444fda`.
- R04 combined case matrix `docs/planning/audits/STEP12_R04_COMBINED_ACCEPTANCE_MATRIX_2026-10-08.md`.
- Final audit/evidence `docs/planning/audits/B01_B06_R04_FINAL_EVIDENCE_2026-10-08.md`.
- R04 final handoff `docs/handoff/current/HANDOFF_STEP_12_BUG_R04_FINAL_2026-10-08.md`.
- Code merge verified `baf3257b293f6b05b4cdbca7e9f3d4aa1272d218`, independent official main CI `37725495137` SUCCESS 192 tests, frozen UI 30/30, Windows portable/Chromium PASS; docs-only status commit excluded from tested implementation SHA.
- R00–R04 offline audit is **COMPLETE**. Manual real Google READY/restart and later live Flow are separate BLOCKED product gates.

## 8 October 2026 — Independent Portable Distribution QA complete
- User confirmed Google **login works**; restart proof `Validasi restart: Lulus` not yet supplied. Live Flow Generate/Download remains BLOCKED.
- Scope approved by user to continue non-login work: strengthen release ZIP verification only, **PASS**.
- PR #18 merged `baff19bb7c28612837d24001b9db9ee4a84251e5`, official main CI `37728080637` SUCCESS: **217 tests**, 30/30 frozen UI, Chromium and Windows portable build/smoke, **real ZIP SHA/CRC/source/path verifier PASS**.
- The new checker caught a real build-order bug: dependency inventory `THIRD_PARTY_NOTICES.txt` used to be generated before cleaning `dist`, causing the distributable ZIP to miss it. Builder now generates the notice after cleaning and requires it.
- ZIP 1,049 files, inner SHA256 `b58bba7b18517f67e6db5a79b299f3bd170a20c5536ab8f11c7d9ed4bfc3a6b2`; source `baff19bb7c28612837d24001b9db9ee4a84251e5`.
- Windows GitHub Actions artifact ID `11528593129`, outer-wrapper SHA256 `17e9c36b2f6db95f99ba5fb9fa3a0e4234dd5c188191c12f625cb1cd105a9431`; expires 22 Oct 2026 UTC.
- Evidence: `docs/planning/audits/STEP12_PORTABLE_RELEASE_INTEGRITY_EVIDENCE_2026-10-08.md`.
- Latest handoff: `docs/handoff/current/HANDOFF_STEP12_PORTABLE_QA_TO_MANUAL_GATE_2026-10-08.md`. R00–R04 offline audit unchanged, no live provider actions.

## 8 October 2026 — SOL independent Hasil export concurrency hardening PASS
- Fixed `ResultManifestWriter.write` concurrent static-temp collision via a uniquely owned NamedTemporaryFile, flush/fsync, atomic same-directory replace and own-temp cleanup.
- Deterministic two-writer barrier regression and injected replace/partial-write failure tests PASS. Previous final manifest survives failed publication; no orphan temp.
- Schema v1.0 and UI unchanged. Concurrent successful exports still have last-writer-wins semantics; no optimistic stale-snapshot fencing claimed.
- PR #19 merged code/tested `42afad61a6bde7798623d807de2c74c51339fe82`; official main CI `37729402213` **SUCCESS**: 220 passed, Ruff/mypy/architecture PASS, UI 30/30 PASS, Chromium + Windows portable/smoke + ZIP verification PASS.
- Windows artifact ID `11529730338` sha256 `ccf0aa7d64ddb967d5732952970aa7785f140fa8f579f4906659869b4d9b7272`, expires 2026-10-22; internal portable ZIP sha256 `242beb868acf5d2e190ba0f746963d607b1493aea258b34213d84fa2714da97d`.
- Evidence `docs/planning/audits/STEP12_MANIFEST_ATOMIC_EXPORT_EVIDENCE_2026-10-08.md`; handoff `docs/handoff/current/HANDOFF_STEP12_MANIFEST_EXPORT_SAFE_2026-10-08.md`.
- User reported Google manual login possible; READY-after-app-restart proof not supplied. Flow live remains BLOCKED, no live actions tested.

## 8 October 2026 — SOL LocalResults late failure regression COMPLETE / PASS
- Fixed a missed R03 history-protection path: `LocalResultsService.record_download_failed` now uses existing atomic `save_failure_if_unconfirmed`, not unconditional `save`, and returns effective persisted state. Confirmed DOWNLOADED history, output path and editing handoff survive late FAILED reports.
- New real SQLite/Workspace/Qt-compatible integration regressions: normal failed outcome, delayed failure after successful download, and cross-service delayed failure. No port/schema/architecture/UI change.
- PR #20 merged code `8149309540233a3a9255b6a2610cfb2554937ed1`, official tested main CI `37730824287` **SUCCESS**: Ruff/mypy/architecture PASS, **223 tests**, **30/30 frozen UI**, staged Chromium + Windows portable build/smoke + verified ZIP PASS.
- Windows artifact ID `11529054245`, SHA256 (outer archive) `a3254d36eafc023647908f790ecc693fdb43e01793fd096aeea502cdb5ecf1c5`; inner ZIP SHA256 `07bd9418bd37eea491e58484650b5e674df18773b0e711343ad187c629bdfb5c`. Artifact expires 22 Oct 2026 UTC.
- Evidence: `docs/planning/audits/STEP12_LOCAL_DOWNLOAD_FAILURE_HISTORY_EVIDENCE_2026-10-08.md`; handoff: `docs/handoff/current/HANDOFF_STEP12_LOCAL_DOWNLOAD_HISTORY_SAFE_2026-10-08.md`.
- Manual Google login reported working but post-restart READY proof absent; all live Google Flow operations still blocked.

## 8 October 2026 — SOL SQLite Download History Read-Only QA COMPLETE / PASS
- Confirmed legacy-project bug: `SqliteDownloadResultRepository.get` / `list_for_episode` previously created missing download_results table on reads. Both now open `mode=ro` and inspect `sqlite_master`; no DDL, legacy DB mutation or accidental creation. Explicit write logic unchanged.
- Real SQLite regressions: missing DB, legacy no-table checksum/no-journal, existing download history checksum, corrupt DB byte preservation all PASS.
- PR #21 merged code `936279f71d1a2863a5b9a0f61923d9b226c1b0a2`; official merged-main CI `37732145080` SUCCESS: **227 pytest**, Ruff/mypy/architecture, frozen UI **30/30**, staged Chromium + Windows portable smoke and ZIP checksum/CRC/source verifier PASS.
- GitHub Windows artifact `11530112083` (outer sha256 `789bb3c1afd5106580180f9b288e4067665b203e5477519ff291f6a8c02e9056`), inner ZIP sha256 `480ef6a8c08036990cf458b8f0c0ec2971aa47a031b29ea12112a461c3f357b6`, expires 22 Oct 2026 UTC.
- Evidence `docs/planning/audits/STEP12_DOWNLOAD_HISTORY_READONLY_EVIDENCE_2026-10-08.md`; handoff `docs/handoff/current/HANDOFF_STEP12_DOWNLOAD_READONLY_2026-10-08.md`.
- User's Google login works per report; READY after full app restart unverified. No Google Flow live test authorized/performed.


## 2026-10-08 — Flow-Otomatis E12 text-first planning alternative (not final DOCX parity)
User authorized publishing TXT/MD instead of requiring manual DOCX upload. Draft PR #23 mirrors:
- V1.0 parent archive: `docs/planning/step12/MASTER_PLAN_FLOW_OTOMATIS_V1_0_ARCHIVE_READABLE_COPY_2026-10-08.md`.
- V1.1 authoritative **content for planning review**: `docs/planning/step12/MASTER_PLAN_FLOW_OTOMATIS_V1_1_READABLE_COPY_2026-10-08.md` and `..._RECONSTRUCTED_2026-10-08.txt`.
- E12-00 audit text: `docs/planning/audits/E12_00_BASELINE_GOVERNANCE_READABLE_COPY_2026-10-08.md` and `...RECONSTRUCTED_2026-10-08.txt`.
- Reconstructed `.docx` files are **not original approved binary/visual reference**; see `docs/planning/audits/E12_00_TEXT_EQUIVALENCE_AND_G0_LIMITS_2026-10-08.md`.
This addition does not supersede the frozen 30-reference UI DOCX or existing Software Factory pre-coding gates. The strict G0 DOCX authority gate remains BLOCKED. Planning review may continue; coding cannot.


## E12-01 proposals — not yet implemented (8 Oct 2026 WIB)
- Candidate ADR-020/021/022/023 in `docs/architecture/`; reviewed source owner inventory and decision matrix: `docs/planning/step12/E12_01_ADR_DECISION_MATRIX_AND_HANDOFF_2026-10-08.md`.
- Local E12-01 Word authoring reference: `E12_01_ASTRA_ARCHITECTURE_ADR_FLOW_OTOMATIS_2026-10-08.docx` (not yet verified as an original DOCX in this repository); Markdown ADRs are the searchable planning proposals, **not code-ready authority**.
- `PROJECT_STATE.md`, `TASKS.md`, `AGENTS.md`, frozen UI 30-state DOCX and overrides, Master Plan V1.0/V1.1 and prior ADRs remain higher-order constraints.
- E12-01 T06 approval outstanding; G0 original DOCX visual parity and external provider G1 remain BLOCKED. No claim of UI implementation or live Flow behavior.
