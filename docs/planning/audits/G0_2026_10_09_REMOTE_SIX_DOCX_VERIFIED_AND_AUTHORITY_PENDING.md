# Flow-Otomatis — G0 six original planning DOCX uploaded and independently verified

**Date:** 2026-10-09 WIB. **Scope:** documentary source integrity and gate bookkeeping only. DRAFT PR #27, no merge/coding/live Google Flow action.

## Remote archival verification: 6/6 PASS

The authenticated Windows G0 Git Bash uploader has now pushed all six original DOCX source candidates onto `docs/g0-original-planning-binaries-20261009`, at upload commit **`3a5fba85114a3f8d22ba4ceda9983de0a6ed3b1a`**.

GitHub `git/trees/<upload commit>?recursive=1` was independently checked against `docs/planning/originals/G0_ORIGINAL_BINARIES_MANIFEST_2026-10-09.json`. The **six expected paths, six Git blob SHA-1 identities, and six exact byte lengths all match (6/6)**. The Git SHA-1 values were computed earlier from the original source bytes, whose SHA-256 and DOCX ZIP integrity tests all PASS. This is **independent verification of remote object identities**, not an unsubstantiated claim that the connector re-downloaded six raw binaries for SHA-256 recalc.

| Source | Bytes | SHA-256 (original) | Git blob SHA-1 (matched GitHub tree) |
|---|---:|---|---|
| E12-00 original 15:20 WIB | 47,457 | `2df71a84b3f33ba3e04114f0508764d9de7d798fa6926b1aa5dfbfbd7f0f5452` | `e9dbf7df40e92cd9b72bcaf56ef015c1a7d3122c` |
| E12-00 handoff 15:21 WIB | 47,452 | `9cc648b90a4c802558f6cea4435770396c926abcb6796897d958424e595ba05e` | `98c0a544d5659207713a7b2333825d7706b83bb3` |
| Master Plan V1.1 original | 79,528 | `ace281206f8f7089643a51328486f6e949c706f1a9c8710fc5f500c664f04f71` | `4f706be5b6027317e8379db87049ca0a8713961e` |
| E12-01 architecture original | 50,750 | `9b3dd7cc9758f135c66541effa878b56a708c9b272d6698a4b92b2d585efc74d` | `17f47cc5e47396d07b39b0c36c7d27e2a90beeba` |
| E12-01 V1.1 ADR review | 54,229 | `0eab21d9664a31d187bb6c168ae47766462ed896e494b95021d10874855d58a3` | `24b8d815e7eedf56e5c54d150a06fe6e1c214152` |
| E12-02 ASTRA prompt pack original | 49,815 | `b8224da4460bb66df3cebba15fc1a4bbdb49c2a293ac80396b2eddbc720fa8ec` | `61cc9bcae36eac9c4621b7df5d270dff18707a98` |

**Total original binary bytes:** 329,231.

## Commit isolation and CI

Compare pre-upload PR head `94a53a6c30876077bf942f8218cf5d92bf583ccd` to real GitHub upload commit `3a5fba85114a3f8d22ba4ceda9983de0a6ed3b1a`: **one commit, seven added files** — six DOCX under `docs/planning/originals/2026-10-08/` and one JSON manifest at `docs/planning/originals/`. No existing source file overwritten, no application code edited. The CI run associated with the upload commit was **in progress at initial verification**; distinguish it from any later successful verification in CI history. The parent `main` remained `5b74d686d44ff67f7473fe46d8fcb7a9904618bf`.

## What changed in gates — and what did not

- **G0 original E12 planning binary preservation subgate: PASS (6/6 on GitHub).** Do **not** ask the owner to upload these six DOCX again.
- **G4 E12-02 owner-approved UI and binary archive: PASS (24/24 already verified in Draft PR #25)**, separate from PR #27.
- **G0 overall remains BLOCKED:** owner/ASTRA selection of canonical source authority, parity of original uncompressed 30-image Word vs pre-existing compressed JPEG reference, and completion of the applicable original planning/source-of-truth checklist are **not** established by mere file presence. Both E12-00 variants are intentionally preserved; difference is timestamp-only (15:20 vs 15:21 WIB) in XML text, but no silent overwrite/authority selection is permitted.
- **E12-01 ADR-020..023 T06 PENDING owner signoff**; Draft PR #26 documents wording clarifications, not approval.
- **G1 provider access policy UNKNOWN/BLOCKED, G5 per-account real credit/tariff UNVERIFIED, G6 READY after full application restart UNVERIFIED.** No live browser/Generate/Download or credit use.
- **No PR merge or new app code, migrations or distribution release** allowed by this archive PASS.

## Controlled follow-up

1. Record original six DOCX SHA manifest in `docs/planning/SOURCE_OF_TRUTH_MANIFEST.md` **on a future explicitly approved integration**; the existing manifest in `main` must not be silently reinterpreted while PR #27 remains DRAFT.
2. Obtain review/authority choices for original 30-UI Word and E12-00/master/E12-01 documents; treat timestamp versions as variants, not competing feature decisions.
3. Keep PR #25, #26, #27 unmerged pending policy and user authorization. Continue planning/validation that does not require coding; do not imply provider permission or account readiness.
