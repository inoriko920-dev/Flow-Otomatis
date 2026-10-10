# G0 — Owner-approved canonical source/reference selection

**Owner signoff date:** 2026-10-09 WIB  
**Project:** `inoriko920-dev/Flow-Otomatis`  
**Decision:** **APPROVED — G0-A, G0-B, and G0-C reference-authority choice**  
**Scope:** identifies which preserved original documents are authoritative for review/visual design; **does not** approve architecture content, implementation, PR merge, real provider operations, or credit usage.

## Explicit owner decision

After the assistant presented the following five recommended reference choices in the conversation, the owner replied **`setuju`** (agree):

| Recommended reference | Final owner decision | Canonical path and verified source |
|---|---|---|
| Original 30 existing frozen UI | **APPROVED** as highest-fidelity **visual authority** | PR #25 `docs/ui/original_uncompressed/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx`, 41,006,814 bytes; SHA-256 `1549d0c9d39d71632abfab15f454fa291a7cdd5c6253453432f87fc5fd57711f`; Git blob `88b08c8c2ef001fc7d22aecd04625a75c206064d` |
| Earlier JPEG-compressed 30 UI DOCX | **APPROVED** as **historical/convenience preview only**, **not exact-parity authority** | `main` `docs/ui/04_STEP_04_FINAL_UI_REFERENCE_FLOW_OTOMATIS_BIOGRAPHY_SYNC_V1_2.docx`, 329,255 bytes; it contains 30 JPEG and differs in 4 of 17 non-media DOCX ZIP entries |
| E12-00 baseline | **APPROVED** **15:21 WIB handoff** as current original baseline authority, preserve 15:20 source for provenance | PR #27 `docs/planning/originals/2026-10-08/E12_00_ASTRA_BASELINE_GOVERNANCE_1521_WIB_HANDOFF_2026-10-08.docx`; SHA-256 `9cc648b90a4c802558f6cea4435770396c926abcb6796897d958424e595ba05e`; Git blob `98c0a544d5659207713a7b2333825d7706b83bb3` |
| Master Plan implementation-ready | **APPROVED** original **V1.1 DOCX** as authoritative planning source for review | PR #27 `docs/planning/originals/2026-10-08/MASTER_PLAN_FLOW_OTOMATIS_V1_1_IMPLEMENTATION_READY_2026-10-08.docx`; SHA-256 `ace281206f8f7089643a51328486f6e949c706f1a9c8710fc5f500c664f04f71`; Git blob `4f706be5b6027317e8379db87049ca0a8713961e` |
| E12-01 architecture planning | **APPROVED** original **V1.1 GitHub Review DOCX** as primary **review draft**, not an adopted architecture | PR #27 `docs/planning/originals/2026-10-08/E12_01_ASTRA_ARCHITECTURE_ADR_V1_1_GITHUB_REVIEW_2026-10-08.docx`; SHA-256 `0eab21d9664a31d187bb6c168ae47766462ed896e494b95021d10874855d58a3`; Git blob `24b8d815e7eedf56e5c54d150a06fe6e1c214152` |

**Supporting/frozen UI constraints still apply:** `docs/ui/IMPLEMENTATION_OVERRIDES.md` takes precedence over accidental/misleading labels in generated artwork; new E12-02 owner-approved 22 PNG designs and final reference DOCX in PR #25 supplement the 30 frozen originals without silently replacing them. No replacement of source bytes, no overwriting the compressed historical copy and no branch merge performed by this decision.

**E12-00 provenance note:** preserve the earlier 15:20 WIB original alongside the chosen 15:21 WIB original; earlier OOXML text-run comparison identified only one-minute timestamp differences, not a materially different policy.

## Gate effects (narrow and exact)

- G0-A: **PASS — owner chose original 30-PNG DOCX as canonical visual authority**. The compressed JPEG copy is no longer a candidate for authoritative pixel or text parity, so **no claim of equivalence is needed or made**. Any downstream agent must read the original before changing UI. The original resides in unmerged **PR #25**, not `main`.
- G0-B: **PASS — owner chose 15:21 E12-00 handoff source**, retains 15:20 as archived alternative. Both original DOCX binaries reside in unmerged **PR #27**.
- G0-C: **PASS — owner chose original Master V1.1 planning source and E12-01 V1.1 review draft**. All original bytes are in unmerged **PR #27**. **Master Plan's separate implementation signoff and E12-01 T06 ADR approval are NOT inferred from choosing the source file**.
- G0 physical preservation: **PASS** on the respective review branches (PR #25: exact 24 UI/doc binaries; PR #27: exact six original planning DOCX).
- **G0 source-authority selection / owner-signoff subgate: PASS**; formal G0 **repository integration / complete pre-code gate remains PENDING** because the chosen canonical binaries and this decision are currently on **separate unmerged draft PRs** and are not yet manifested as effective source on `main`. There may be other governance/STEP 00–07 obligations; do not claim entire pre-code G0 gate PASS from this signoff alone.
- **E12-01 T06 (ADR-020/021/022/023): PENDING separate explicit content/contract approval.**
- **G1 provider automated multi-account authorization: UNKNOWN/BLOCKED. G5 actual per-account credit/price: UNVERIFIED. G6 login READY after full application restart: UNVERIFIED.**
- **NO app code, migrations, production browser automation, live Google Flow Generate/Download, credit usage, PR merges or distribution release authorized by this source-selection approval.**

## Next allowed review work

1. On this draft branch, index the owner-approved reference precedence in `docs/planning/SOURCE_OF_TRUTH_MANIFEST.md` with clear **review-branch-only** scope and PR #25 cross-links; do not alter `main` or the approved DOCX/PNG bytes.
2. Review E12-01 V1.1 and the separate PR #26 wording clarifications; prepare a concise T06 acceptance summary for a **future distinct owner decision**. Preserve fake-only tests and policy restrictions.
3. Keep G1/G5/G6 evidence status clearly separated; no provider claims without real authorized evidence.

**Approval evidence:** The owner was asked whether they agreed with the previously presented five reference choices, and explicitly answered `setuju`. This record preserves exactly that scope.
