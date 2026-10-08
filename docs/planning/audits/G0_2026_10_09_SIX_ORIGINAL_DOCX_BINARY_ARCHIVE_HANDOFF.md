# Flow-Otomatis G0 — Preserve six exact original planning DOCX (review only)

**Date:** 2026-10-09 WIB | **GitHub target:** `inoriko920-dev/Flow-Otomatis`, branch `docs/g0-original-planning-binaries-20261009` | **Status:** LOCAL QA PASS / REMOTE BINARY UPLOAD PENDING / G0 NOT PASS.

## Scope and purpose

These are the actual DOCX binary artifacts of STEP 12 planning E12-00/01/02 and implementation-ready Master V1.1. Existing versions in `docs/planning` are partly **reconstructed text-equivalent**, not the exact original bytes. Preserve original variants **without overwriting** reconstructed files, source code, frozen UI screenshots, or main. Never infer T06 owner approval from a binary upload.

**Independent source manifest** (both hash algorithms are from original ZIP/DOCX bytes, not a re-render):

| Candidate source ID | Exact file size | SHA-256 | Expected Git blob SHA-1 |
|---|---:|---|---|
| E12-00 15:20 WIB original | 47,457 | `2df71a84b3f33ba3e04114f0508764d9de7d798fa6926b1aa5dfbfbd7f0f5452` | `e9dbf7df40e92cd9b72bcaf56ef015c1a7d3122c` |
| E12-00 15:21 WIB handoff | 47,452 | `9cc648b90a4c802558f6cea4435770396c926abcb6796897d958424e595ba05e` | `98c0a544d5659207713a7b2333825d7706b83bb3` |
| Master Plan V1.1 implementation-ready | 79,528 | `ace281206f8f7089643a51328486f6e949c706f1a9c8710fc5f500c664f04f71` | `4f706be5b6027317e8379db87049ca0a8713961e` |
| E12-01 ADR original | 50,750 | `9b3dd7cc9758f135c66541effa878b56a708c9b272d6698a4b92b2d585efc74d` | `17f47cc5e47396d07b39b0c36c7d27e2a90beeba` |
| E12-01 ADR V1.1 GitHub review | 54,229 | `0eab21d9664a31d187bb6c168ae47766462ed896e494b95021d10874855d58a3` | `24b8d815e7eedf56e5c54d150a06fe6e1c214152` |
| E12-02 ASTRA UI prompt pack (22 images) | 49,815 | `b8224da4460bb66df3cebba15fc1a4bbdb49c2a293ac80396b2eddbc720fa8ec` | `61cc9bcae36eac9c4621b7df5d270dff18707a98` |

E12-00 variants have the same 279 Word text runs except a **15:20 versus 15:21 WIB timestamp** in document/header; both must be kept until source-authority is signed off. The uploaded original 30-UI reference and owner-approved 22 UI **already live in PR #25**, G4 archival PASS; **do not upload those assets again**.

## Prepared ZIP and exact operation

One ChatGPT-local artifact `FLOW_OTOMATIS_G0_6_DOCX_ASLI_UPLOAD_GIT_BASH_2026-10-09.zip`:

- ZIP **321,122 bytes**, SHA-256 **`34f5106a9ff926d3c25e8029bf4378a4bfb59b9563bbbdf3b49f4657f6884507`**; 12 entries, ZIP CRC PASS.
- Has six byte-identical DOCX under `PAYLOAD/`, SHA256 TSV, JSON manifest, `UPLOAD_G0_ORIGINAL.sh`, `CEK_G0_GIT_BASH.cmd` and `UPLOAD_G0_GIT_BASH.cmd` for already-installed Git Bash on Windows 11.
- Destinations are **only** `docs/planning/originals/2026-10-08/*.docx` plus `docs/planning/originals/G0_ORIGINAL_BINARIES_MANIFEST_2026-10-09.json` on **this PR branch only**, never `main`.
- Provenance source is the original DOCX local files plus `FLOW_OTOMATIS_G0_DOCX_FOR_PR23_2026-10-08.zip` E12-00 15:21 variant. No reconstruction, no re-save of DOCX, no overwritten historical files.
- User operation (only if needed): extract ZIP; run `CEK_G0_GIT_BASH.cmd` until 6/6 PASS, then `UPLOAD_G0_GIT_BASH.cmd`; existing Git config/GitHub login should work, report SHA. This performs **no merge**.

## Tests actually run

1. All 6 source DOCX ZIP CRC: **PASS**.
2. **6/6 original SHA-256 and Git blob SHA-1**: **PASS**. Shell syntax `bash -n`: PASS. Archive ZIP CRC: PASS.
3. Actual **isolated local bare Git remote** end-to-end: clone target test branch -> stage **7 docs-only files** -> commit -> push -> compare remote HEAD -> Git object 6/6: **PASS**, local test commit `24bbd810e140b39b528d8f662b8e9b1d77656eb9` (**not a GitHub commit**).
4. Idempotent second run: remote commit SHA unchanged: **PASS**.
5. Changed source DOCX bytes intentionally: `--verify` blocked changed size, then source restored and **6/6 PASS**.

**Not performed:** real Windows upload to GitHub, original binary presence in this draft branch. Thus **G0 original planning binary archival subgate PENDING**.

## G0 and implementation safety

- A physical original 30-UI DOCX exists in PR #25, but it is **not internally identical** to the older JPEG-compressed copy on main; source-of-truth visual authority decision and parity still require review.
- Saving original planning binaries does not automatically decide their authority, close G0, approve ADR T06, prove provider G1 permissions, G5 credits, or G6 restart READY.
- **Keep PR DRAFT, no merge and no application code, browser automation, live Generate/Download, or credit spending.**

## 9 October 2026 — POST-UPLOAD CORRECTION: all six remote binaries PASS
The previous statements `REMOTE BINARY UPLOAD PENDING`, `NOT yet committed` and `6 DOCX still need Windows upload` above refer to the **pre-upload state only** and are now **superseded**. Actual authenticated Windows GitHub upload commit: `3a5fba85114a3f8d22ba4ceda9983de0a6ed3b1a`. GitHub REST tree and `G0_ORIGINAL_BINARIES_MANIFEST_2026-10-09.json` independently show **6/6 exact paths, git blob IDs and lengths PASS**, seven added docs-only paths, no overwritten source. Full new record: `docs/planning/audits/G0_2026_10_09_REMOTE_SIX_DOCX_VERIFIED_AND_AUTHORITY_PENDING.md`. **Original binary archival subgate PASS; no further DOCX upload needed.** G0 authority/visual parity, T06, G1, G5 and G6 **not** automatically PASS. No merge or code.
