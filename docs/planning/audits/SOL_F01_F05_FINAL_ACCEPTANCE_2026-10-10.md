# SOL F01–F05 — final automated acceptance evidence (10 October 2026)

**Scope:** ASTRA 10 October F01–F05 offline audit remediation only; fixes implemented by SOL on Draft PR #34. No added feature, approved UI changes, live Flow Generate/Download, credentials, credits, or release.

## Reproducible source
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `sol/uix22-polish-main-entry-20261009` / Draft PR #34
- Tested code and handoff SHA: `5bf069b6fcdd02f2aa4db4816340096827e3cef8`
- GitHub Actions: https://github.com/inoriko920-dev/Flow-Otomatis/actions/runs/38048857517
- Workflow status: completed / **SUCCESS**. Five separate Windows jobs all **SUCCESS**.

## Final job gates
| Job | Job ID | Result | Actual coverage |
| --- | --- | --- | --- |
| `quality` | `114203757164` | PASS | Python 3.14.7 / uv, Ruff formatting/lint, mypy (91 source files), architecture guard, **703 tests PASS** |
| `offline-simulator-windows` | `114204059635` | PASS | synthetic allocation CLI, separate Windows simulator GUI packaging and file verification |
| `uix22-qt-windows` | `114204059637` | PASS | 22 real Qt states, integrated desktop/laptop screenshots, frozen reference checksum and UI preview checks |
| `ui-visual` | `114204059641` | PASS | 30 real UI states compared with frozen references |
| `package-windows` | `114204201341` | PASS | Chromium staging/smoke, pinned 22 UI assets, PyInstaller portable onedir ZIP, executable smoke and release ZIP source/CRC/Windows-path validation |

## Artifacts — all belong to tested commit `5bf069b...`
| Type | GitHub artifact ID | Size (bytes) | SHA-256 (GitHub artifact digest) |
| --- | --- | --- | --- |
| Portable Windows ZIP | `11668289455` | `465495389` | `013efbc9625231752b9628db305347809c8bfb4e075f9af5c2e6faf8f6cb1c99` |
| UI integrated screenshots / preview | `11668717421` | `104803176` | `17c41c82eed0858a9edc549537b9d30e498c098c7c648933dc3c129e52864ec2` |
| Offline simulator Windows | `11668124305` | `13229894` | `bc041cb7489e677fb70601a05723fccc1685a9f5b31da0be36ee0f449ab75347` |
| UI comparison evidence | `11667869629` | `3316911` | `3579e29c2ee076c15aa517636b718b3bd70e62a00838e619e45e9110a523eb3c` |

The above hashes are GitHub-reported ZIP artifact digests, **not** a separately downloaded independent SHA-256 recomputation. All four artifacts were reported unexpired, with GitHub artifact expiry on **24 October 2026 UTC**. They are temporary CI artifacts, **not** a published software release.

## F01–F05 mapping to final verified coverage
- **F01** — Import `created_at` requires explicit timezone. Naive timestamps fail before project writes; aware `Z`, positive and negative offsets accepted; old data remains unchanged.
- **F02** — Generation queue stores fixed allowlisted/sanitized messages rather than raw provider exception or driver details. Tests cover simulated credentials, signed links, generic/auth/cancel/ambiguous failure.
- **F03** — Results snapshots, `record_downloaded`, SQLite atomic Download persistence, and cached MP4 reuse reject persisted jobs whose request fields differ from current Scene. Historical MP4 and Download records remain untouched. Synthetic changed-duration/prompt/image/profile and race tests PASS.
- **F04** — Proven `SAFE_FAILURE` is represented by a typed error and marks a safe failed request requiring explicit reprepare; unknown/contradictory evidence and no stable ID stay `ATTENTION_REQUIRED / SUBMIT_AMBIGUOUS`. No blind retries or live Flow selector mutations.
- **F05** — Reading Generation history uses read-only SQLite and does not migrate. Unsupported future marker fails closed; legacy decoding is non-mutating. Explicit mutating recovery/prepare performs guarded migration and rollback on injected failure.

## Gate declaration
**F01–F05 = CLOSED for the audited, automated offline acceptance scope at SHA `5bf069b...`.** This does **not** establish full application completion, real Google account login persistence, real Google Flow project/Generate/Download success, provider eligibility, or owner-machine acceptance.

Independent upstream/project gates remain **BLOCKED / UNVERIFIED** as applicable: original strict G0 document-equivalence concern, account-specific READY-after-restart, I12-02B2-LIVE and I12-03-LIVE. PR #34 remains **Draft/unmerged**. No new features, UI changes, or paid provider calls are approved by this signoff.

## Handoff
No further changes are required **for these five audited offline findings** unless a reproducible regression appears. Continue app development only within previously approved work scope; do not merge broad PR #34 or claim production-ready solely from offline CI.
