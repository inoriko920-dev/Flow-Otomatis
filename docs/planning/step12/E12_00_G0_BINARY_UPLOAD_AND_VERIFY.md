# E12-00 / G0 — Original DOCX upload and verification (pending)

**State: BLOCKED.** Do not merge PR #23 or mark E12-00 PASS until both original DOCX binaries exist on this branch and are verified. Do not edit application code or launch Google Flow.

Destination repository: `inoriko920-dev/Flow-Otomatis` only.
PR: https://github.com/inoriko920-dev/Flow-Otomatis/pull/23
Target branch: `docs/e12-00-v11-review-20261008`.
Current main baseline: `e560684e04ed3a5fad40bb00a91823de68ca5431`.

## Authoritative files (from the final E12-01 handoff ZIP)

| Repository path | Bytes | SHA-256 | Expected Git blob SHA-1 |
|---|---:|---|---|
| `docs/planning/step12/MASTER_PLAN_FLOW_OTOMATIS_V1_1_IMPLEMENTATION_READY_2026-10-08.docx` | 79528 | `ace281206f8f7089643a51328486f6e949c706f1a9c8710fc5f500c664f04f71` | `4f706be5b6027317e8379db87049ca0a8713961e` |
| `docs/planning/audits/E12_00_ASTRA_BASELINE_GOVERNANCE_FLOW_OTOMATIS_2026-10-08.docx` | 47452 | `9cc648b90a4c802558f6cea4435770396c926abcb6796897d958424e595ba05e` | `98c0a544d5659207713a7b2333825d7706b83bb3` |

**Important:** An older standalone E12-00 DOCX copy was found with SHA-256 `2df71a84b3f33ba3e04114f0508764d9de7d798fa6926b1aa5dfbfbd7f0f5452`, 47457 bytes. Its substantive text matches the ZIP version except two document-generation timestamps (15:20 vs 15:21 WIB). To avoid ambiguity use **the E12-00 DOCX inside the final handoff ZIP** (SHA256 `9cc648...`). The earlier copy is not the upload target.

## Upload steps

1. Use the files supplied in the chat's `FLOW_OTOMATIS_G0_DOCX_FOR_PR23_2026-10-08.zip`. Extract it locally.
2. In GitHub navigate to **Code**, select branch `docs/e12-00-v11-review-20261008` (do not select `main`).
3. Navigate to `docs/planning/step12/`, choose **Add file → Upload files**, upload the V1.1 DOCX, commit to the same review branch.
4. Navigate to `docs/planning/audits/`, upload the E12-00 DOCX, commit to the same review branch.
5. Check GitHub blob IDs against the exact SHA-1 values above; these are SHA-1 Git *blob* content hashes, not SHA256 checksums.
6. After verification update this checklist, `TASKS.md`, `PROJECT_STATE.md`, and PR evidence; only then assess G0/PR merge eligibility.

## Outstanding gates

G0 docs: **BLOCKED** pending DOCX binaries and GitHub verification.
G1 policy and live Google Flow: **BLOCKED/UNVERIFIED**.
Restart `READY` across application instances: **UNVERIFIED**.
E12-01 planning DOCX exists locally but is not authorization for coding; proceed with one wave/gate at a time.
