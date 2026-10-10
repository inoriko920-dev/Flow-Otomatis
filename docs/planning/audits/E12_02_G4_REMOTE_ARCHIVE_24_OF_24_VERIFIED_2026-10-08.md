# E12-02 G4 — Remote archive verified, 24/24 immutable binaries on Draft PR #25

**Date:** 2026-10-08 WIB. Independent check against GitHub PR branch commit `6fc332e10ee0109e200c152724a4deeb5978aa3c` (the actual Windows Git Bash V3 upload). **This is a new status update; earlier PENDING / 0/24 statements are historical pre-upload snapshots.**

## Final G4 archival evidence — PASS

1. Actual GitHub REST branch tree contains **22 PNG + FINAL DOCX + original 30-image G0 DOCX = 24/24**, all paths and sizes correct.
2. Computed `git hash-object` IDs from the **exact 24 approved source bytes** in V3 ZIP (`sha1("blob " + byte_count + NUL + bytes)`) and matched **24/24** to GitHub REST tree `blob.sha` and `size`. Source V3 ZIP passes CRC and its `PAYLOAD/MANIFEST_PR25.json` SHA-256 entries match 24/24 source file bytes. This identifies the GitHub binaries byte-for-byte without depending on the connector's binary fetch decoder.
3. `4dfe867079d8c4efc93f00d186eb95031e8ebdc2..6fc332e10ee0109e200c152724a4deeb5978aa3c` compare: **exactly one commit and 25 additions**, all under `docs/ui/` (22 PNG + 2 DOCX + 1 metadata JSON); no existing files rewritten, no app code touched, no merge.
4. **GitHub Actions CI for upload commit** `6fc332e10ee0109e200c152724a4deeb5978aa3c`: `completed/success`.
5. `main` at verification: `5b74d686d44ff67f7473fe46d8fcb7a9904618bf`, unchanged. PR #25 **OPEN/DRAFT**, **NOT MERGED**.
6. The original 30-image reference was added only to `docs/ui/original_uncompressed/`. It **did not overwrite** the prior smaller intentionally compressed reference in `docs/ui/`.

**Approved FINAL DOCX SHA-256:** `9a84372cbb10ad5e2db2d070c1d20319759aabee11ff85324a1193544ec6f1dd` (29,674,786 bytes). **Original 30-image DOCX SHA-256:** `1549d0c9d39d71632abfab15f454fa291a7cdd5c6253453432f87fc5fd57711f` (41,006,814 bytes).

## Exact 24 Git object IDs (verified)

| Asset | Repository path | Git blob SHA-1 | Bytes |
|---|---|---|---:|
| FINAL_DOCX | `docs/ui/final/FLOW_OTOMATIS_E12_02_REFERENSI_UI_FINAL_22_DESAIN_DISETUJUI_2026-10-08.docx` | `1adc62990b00c30e9c30541ca4b263255faf5d2a` | 29674786 |
| G0_ORIGINAL_DOCX | `docs/ui/original_uncompressed/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx` | `88b08c8c2ef001fc7d22aecd04625a75c206064d` | 41006814 |
| UIX-01-A | `docs/ui/final/assets/Flow_Otomatis_UIX_01_A_KOREKSI_12_DARI_60_2026-10-08.png` | `c605a51f2860b48198ecebcddd1e664a4bee3113` | 1936374 |
| UIX-01-B | `docs/ui/final/assets/Flow_Otomatis_UIX_01_B_PARTIAL_INVALID_DRAFT_2026-10-08.png` | `ed6d3049beac8a372384df3e17b3a0907bde8659` | 1393991 |
| UIX-01-C | `docs/ui/final/assets/Flow_Otomatis_UIX_01_C_KREDIT_TARIF_BELUM_TERVERIFIKASI_DRAFT_2026-10-08.png` | `9907e042cb55f047e7f4df3ee6c098d12cb6345c` | 1933915 |
| UIX-02-A | `docs/ui/final/assets/Flow_Otomatis_UIX_02_A_SMART_CREDIT_PLAN_DRAFT_2026-10-08.png` | `42ad6dc7ad5fa5041d49c5082393c2aef1dd931e` | 1159649 |
| UIX-02-B | `docs/ui/final/assets/Flow_Otomatis_UIX_02_B_KREDIT_TIDAK_CUKUP_DRAFT_2026-10-08.png` | `9b64477eaf38e3e79c58ca220b796bb20bf7cf95` | 1293071 |
| UIX-02-C | `docs/ui/final/assets/Flow_Otomatis_UIX_02_C_TIDAK_ADA_AKUN_MEMENUHI_SYARAT_DRAFT_2026-10-08.png` | `082a2016a518c76ab3aa6695e3e0394b2c812d03` | 1268437 |
| UIX-03-A | `docs/ui/final/assets/Flow_Otomatis_UIX_03_A_RINCIAN_KREDIT_PER_AKUN_DRAFT_2026-10-08.png` | `757134508fc1d2280298649c949122743193418a` | 1622897 |
| UIX-03-B | `docs/ui/final/assets/Flow_Otomatis_UIX_03_B_KREDIT_KADALUWARSA_MANUAL_TIDAK_DIKETAHUI_DRAFT_2026-10-08.png` | `1b82b7bf55d803e7573995a8760bd7988d08cba2` | 1610129 |
| UIX-04-A | `docs/ui/final/assets/Flow_Otomatis_UIX_04_A_FREEZE_PLAN_APPROVAL_DRAFT_2026-10-08.png` | `227361abaa6d8453dacd06d3fc95685520964ec6` | 1218093 |
| UIX-04-B | `docs/ui/final/assets/Flow_Otomatis_UIX_04_B_REVISI_KEDALUWARSA_DRAFT_2026-10-08.png` | `972a604ea9e29622dce9cbbe9f8e30ad22f73348` | 1233350 |
| UIX-05-A | `docs/ui/final/assets/Flow_Otomatis_UIX_05_A_RUN_MONITOR_SIMULASI_DRAFT_2026-10-08.png` | `47a4f4ad362e86959836489aaaa8ba81ce061bb4` | 1404624 |
| UIX-05-B | `docs/ui/final/assets/Flow_Otomatis_UIX_05_B_RUN_MONITOR_JEDA_PARSIAL_DRAFT_2026-10-08.png` | `98450c94eb4139d119c7d468602d44446c7f8912` | 1466014 |
| UIX-05-C | `docs/ui/final/assets/Flow_Otomatis_UIX_05_C_SUBMIT_UNCERTAIN_DRAFT_2026-10-08.png` | `5db68a950d92d33dd7bfb00b5e620af57bd93ffc` | 1493533 |
| UIX-06-A | `docs/ui/final/assets/Flow_Otomatis_UIX_06_A_RECOVERY_SUBMIT_UNCERTAIN_DRAFT_2026-10-08.png` | `02c254a4950dff89835bf4198f617ef571b4f63a` | 1240559 |
| UIX-06-B | `docs/ui/final/assets/Flow_Otomatis_UIX_06_B_KONFLIK_LOGIN_KREDIT_DRAFT_2026-10-08.png` | `f81d88a338c7b1cb8b47b9509c9166a3e3837d69` | 1258978 |
| UIX-06-C | `docs/ui/final/assets/Flow_Otomatis_UIX_06_C_HASIL_GENERATE_DITEMUKAN_DRAFT_2026-10-08.png` | `3a247c7fbd3e6a3b4950d6fb4735e728b2859eaa` | 1237414 |
| UIX-07-A | `docs/ui/final/assets/Flow_Otomatis_UIX_07_A_PARTIAL_REPLAN_DRAFT_2026-10-08.png` | `61efadf1ecab1a86a15b7c8624e6559174f16507` | 1214947 |
| UIX-07-B | `docs/ui/final/assets/Flow_Otomatis_UIX_07_B_SCENE_TERKUNCI_DRAFT_2026-10-08.png` | `02c33f61b4f94773a302cbeacf3297e6c29c568f` | 1212644 |
| UIX-08-A | `docs/ui/final/assets/Flow_Otomatis_UIX_08_A_TARIF_KEDALUWARSA_DRAFT_2026-10-08.png` | `9ec9e67d929a7a9c748d457d54dd4ea8f352bb08` | 1188942 |
| UIX-08-B | `docs/ui/final/assets/Flow_Otomatis_UIX_08_B_KEBIJAKAN_BELUM_TERVERIFIKASI_DRAFT_2026-10-08.png` | `9375d0c1b773a64fba65f8da2e5f6a389e43e1e5` | 1222417 |
| UIX-09-A | `docs/ui/final/assets/Flow_Otomatis_UIX_09_A_HASIL_PARSIAL_DRAFT_2026-10-08.png` | `59dfbb577eae271a9aca6865058434f3cfae47e3` | 1051007 |
| UIX-09-B | `docs/ui/final/assets/Flow_Otomatis_UIX_09_B_HANDOFF_12_DARI_60_DRAFT_2026-10-08.png` | `d802a247e02946d9f10281feb15012e732a8ebe1` | 1093226 |

## Gate decisions

- **E12-02 22/22 visual acceptance PASS** (previous explicit owner approval).
- **E12-02 final reference DOCX PASS**, approved 22 PNG embedded unchanged (previous local verification).
- **E12-02/G4 UI binary archival subgate: PASS, independently verified 24/24 on GitHub at the upload commit.** UI reference archive checklist is complete; no further upload required.
- **G0 strict still BLOCKED/PENDING**: merely preserving the original 30-reference DOCX does not establish visual-authority parity with the compressed repo copy or finish archival of all original planning DOCX.
- **G1 provider permission UNKNOWN/BLOCKED; G5 live account credit/price UNVERIFIED; G6 per-account READY after app restart UNVERIFIED; E12-01 T06 owner decision PENDING; migration/live gates remain blocked.**
- **NO source coding, PR merge, real browser Generate/Download or credit use authorized by this archive PASS.**

**GitHub verification result:** 24/24 MATCH; **local V3 ZIP** source CRC/hash PASS; **CI** SUCCESS; documentation-only asset commit; **gate remainder** explicitly not inferred from this proof.
