# G0 strict — independent authority audit after E12-02 24/24 upload

**Audit written 2026-10-09 WIB.** Branch: `docs/e12-02-uix-prompt-only-20261008`, **PR #25 remains DRAFT/unmerged**. This is a factual source-of-truth comparison only, **not an owner approval or coding authorization**.

## 1. E12-02 binary archive is DONE (G4 subgate PASS)

GitHub branch contains 22 owner-approved PNGs + 27-page final 22-UI DOCX + the original 30-UI reference DOCX. At upload commit `6fc332e10ee0109e200c152724a4deeb5978aa3c`: **24/24 exact Git blob SHA-1/size matches approved source**, CI SUCCESS, only 25 `docs/ui/` files added, `main` unchanged. Canonical evidence: `docs/planning/audits/E12_02_G4_REMOTE_ARCHIVE_24_OF_24_VERIFIED_2026-10-08.md`.

**Do not request another upload of the same 24 files.**

## 2. G0 old reference: structural equivalence is NOT established

Two separate DOCX sources exist:

| Source | Repository location | Bytes | Git blob SHA-1 |
|---|---|---:|---|
| Original frozen 30 UI (PNG images) | `docs/ui/original_uncompressed/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx` (PR #25) | 41,006,814 | `88b08c8c2ef001fc7d22aecd04625a75c206064d` |
| Earlier deliberately compressed 30 UI (JPEG images) | `docs/ui/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx` (`main`) | 329,255 | `6e93a7e654e84ba2dd37af1fbc31c68ce3107f26` |

Exact original binary SHA-256: `1549d0c9d39d71632abfab15f454fa291a7cdd5c6253453432f87fc5fd57711f`, preserved without overwrite. Original DOCX 30 media files are **PNG**, resolution **1672×941** each, combined raw-media bytes **46,192,516**. GitHub compressed DOCX contains **30 JPEG**, combined raw-media bytes **304,570**. Both contain **47 DOCX ZIP entries**.

Comparing *ZIP central-directory CRC-32 and uncompressed-size* for the **17 non-image items** (original independently inspected; GitHub compressed file fetched with base64, central-directory parsed without modifying contents):

- **13/17** non-image XML/metadata items matched both CRC and uncompressed byte length.
- **4/17 differed**:

| Internal DOCX item | Original bytes / CRC-32 | GitHub compressed bytes / CRC-32 |
|---|---|---|
| `[Content_Types].xml` | 1,788 / `d0aea7fc` | 1,789 / `b36da929` |
| `word/document.xml` | 117,201 / `6093fef8` | 38,809 / `0784b0dd` |
| `word/_rels/document.xml.rels` | 5,237 / `07b248d5` | 5,237 / `9d469431` |
| `word/styles.xml` | 349,614 / `6226df88` | 349,534 / `966259b1` |

**Conclusion:** both DOCX files contain 30 images but they are **not internally byte-equivalent**, not just the image bytes. The compressed copy changes the media format and document XML relationships/styles; **layout, text and visual equivalence have NOT been proven**. CRC/entry counts do not establish visual parity. **Do not call G0 PASS** just because the compressed reference has 30 image slots.

**Safe proposed resolution (requires owner review):** use the original 30-UI DOCX now archived in `docs/ui/original_uncompressed/` as highest-resolution visual authority (while retaining frozen `docs/ui/IMPLEMENTATION_OVERRIDES.md` and prior approved product scope); consider the compressed copy a historical convenience reference only. Avoid silently switching the authoritative reference path or replacing the existing `main` file before explicit governance signoff.

## 3. G0 original planning DOCX: reconstructed copies are NOT proof of original provenance

The repository currently includes:

- `docs/planning/audits/E12_00_ASTRA_BASELINE_GOVERNANCE_RECONSTRUCTED_2026-10-08.docx`, **35,179 bytes**, a reconstruction, not original binary;
- `docs/planning/step12/MASTER_PLAN_FLOW_OTOMATIS_V1_1_RECONSTRUCTED_2026-10-08.docx`, **181,209 bytes**, a reconstruction;
- `docs/planning/SOURCE_OF_TRUTH_MANIFEST.md` confirms earlier STEP 00–07 source files are committed but distinguishes reconstructed E12 files from original provenance.

Original/candidate Word files available in the project's conversation working artifacts and **not found by exact Git blob SHA-1 on PR #25**:

| Candidate original/copy | Bytes | Git blob SHA-1 | Authority status |
|---|---:|---|---|
| `E12_00_ASTRA_BASELINE_GOVERNANCE_FLOW_OTOMATIS_2026-10-08.docx` working-file variant | 47,457 | `e9dbf7df40e92cd9b72bcaf56ef015c1a7d3122c` | Needs owner/ASTRA selection |
| E12-00 file inside `FLOW_OTOMATIS_G0_DOCX_FOR_PR23_2026-10-08.zip` | 47,452 | `98c0a544d5659207713a7b2333825d7706b83bb3` | **DIFFERS by 5 bytes**; do not guess which is authoritative |
| `MASTER_PLAN_FLOW_OTOMATIS_V1_1_IMPLEMENTATION_READY_2026-10-08.docx` from G0 ZIP | 79,528 | `4f706be5b6027317e8379db87049ca0a8713961e` | Original candidate; not in repo |
| `E12_01_ASTRA_ARCHITECTURE_ADR_FLOW_OTOMATIS_2026-10-08.docx` | 50,750 | `17f47cc5e47396d07b39b0c36c7d27e2a90beeba` | Not in repo |
| `E12_01_ASTRA_ARCHITECTURE_ADR_V1_1_GITHUB_REVIEW_2026-10-08.docx` | 54,229 | `24b8d815e7eedf56e5c54d150a06fe6e1c214152` | Not in repo |

All listed DOCX/ZIP local files passed ZIP CRC inspection. This audit makes **no claim** that the candidates are all required final authorities; selection/provenance and any additional original documents require explicit review. Additional existing STEP 00–07 original DOCX files are already tracked in source-of-truth manifest.

## 4. Decision matrix — do not confuse gates

| Gate | Latest evidence | Status |
|---|---|---|
| G4 E12-02 owner visual approval + binary archive | 22/22 approval, 24/24 exact Git blobs, successful CI | **PASS (archival subgate)** |
| G0 reference original physical archive | 30-image original committed with SHA verified | **PASS for existence and integrity only** |
| G0 frozen 30-UI authority parity | Main compressed differs from original in 4 XML/metadata items and image encoding | **BLOCKED: authority decision/visual QA required** |
| G0 E12 planning originals | Reconstructed copies present; candidates exist locally, original selection + preservation incomplete | **BLOCKED** |
| E12-01 T06 ADR decision | Proposed ADRs, reviewed errata in Draft PR #26, CI PASS | **PENDING owner decision** |
| G1 automated multi-account provider permission | No explicit authorization | **UNKNOWN/BLOCKED** |
| G5 actual tariffs and per-account credit proof | Nominal public rates documented, account evidence absent | **UNVERIFIED** |
| G6 READY after full app restart | Human sign-in alone is not restart evidence | **UNVERIFIED** |

## 5. Recommended next controlled actions

1. **Do not upload 24 UI files again.** They are archived and verified.
2. Record owner/ASTRA choice of **original 30-UI DOCX** vs compressed historical copy as authority; do visual parity review only if retaining compressed as implementation reference. Never overwrite either without explicit authorization.
3. Identify exact authoritative E12-00, master V1.1, E12-01 original planning DOCX versions; require original binary archiving, not reconstructed text substitution. Do not infer approval from `lanjutkan`.
4. Review ADR T06 and provider G1/G5/G6 as independent gating actions, keeping fake tests distinct from real provider actions.
5. **No coding / schema migration / live Generate / multi-account dispatch / credit usage / merge until all independent gates PASS**.
