# HANDOFF — STEP 12 AUDIT A00 → A01

## Gate
A00 — Source-of-truth synchronization and baseline verification: **PASS**.

This handoff is for the audit-remediation track inside STEP 12. It does not supersede the current live-integration handoff and does not unblock I12-02B2-LIVE.

## Baseline
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- ASTRA audit baseline: `e6724a0a5c3d68789149ed5c7eb094d44c9f0967`
- A00 documentation-sync commit: `bc550e57407d1be09fceb64eadd18217f4d9c37c`
- Original uploaded audit DOCX: 48486 bytes, SHA-256 `1011693e1e67673a4af49378ca2009e93f596a74f563276ae060ebcaae0ca210`
- Repository compact text-equivalent DOCX: 10028 bytes, SHA-256 `39ee9d8c37aa573f019649b7f6f04c76812e80cf88b397e5694e0c96f9946527`

## A00 work completed
- committed a validated compact text-equivalent copy of the ASTRA audit DOCX under `docs/planning/audits/`; the original uploaded source hash is retained separately for provenance;
- added the audit index and source-of-truth manifest entry;
- recorded ADR-015 for atomic workspace create/update semantics;
- recorded ADR-016 for queue request revision/fingerprint plus owner/lease recovery;
- recorded ADR-017 for Browser Worker ownership and non-blocking Qt command boundary;
- detected and repaired a truncated first DOCX upload; the replacement DOCX preserves all logical audit text, opens successfully, and rendered cleanly to five pages;
- verified no production source/test/runtime file changed from the ASTRA baseline during A00.

## Official baseline evidence
- CI run: `37639865121`
- Quality job: `112855631708` — SUCCESS
- Windows Server 2025
- CPython 3.14.7 x64
- uv 0.12.23
- frozen sync PASS
- Ruff format PASS — 123 files already formatted
- Ruff lint PASS
- mypy PASS — 63 source files
- architecture guard PASS
- pytest PASS — 90 passed, 1827 warnings

Evidence file:
- `docs/planning/audits/A00_BASELINE_EVIDENCE_2026-10-07.md`

## Findings that still apply
All six findings remain open because A00 changed documentation only:
- F01 missing prompt TXT can still be accepted as READY;
- F02 duplicate import can still preserve stale generation/download data;
- F03 queued request can still mix stale and current state;
- F04 corrupt scene rows can still break project listing;
- F05 Google-session checking can still block the Qt UI thread;
- F06 orphan RUNNING jobs still lack real recovery.

## Next package — A01 only
Owner focus:
- EpisodePackageReader;
- EpisodeImportService;
- WorkspaceRepositoryPort;
- SqliteWorkspaceRepository;
- nearest import/UI integration tests.

A01 must:
- reject missing `.txt` prompt references in ZIP and folder packages with typed `PROMPT_FILE_MISSING` behavior before save;
- add atomic create semantics that reject duplicate episode/project identity;
- preserve the legitimate update path used by scene planning;
- never delete/reset old jobs, downloads, or export state merely to make duplicate import succeed;
- add/adjust safe Indonesian UI error handling;
- prove failed import changes no project/jobs/downloads;
- preserve existing duration and ZIP traversal behavior.

A01 gate is defined by the ASTRA audit. Do not start A02 in the same package.

## Safety boundary
- Frozen UI remains authoritative; no redesign.
- Flow duration remains 4/6/8/10.
- Audio/SRT Target remains authoritative.
- Generate and Download remain separate.
- Ambiguous external submit is never blindly retried.
- I12-02B2-LIVE stays BLOCKED until real-account restart validation passes.

## Instruction to next SOL
Verify `main` has not advanced unexpectedly, read ADR-015 and the A01 section of the audit, implement only A01, run the required targeted plus regression gates, update state/handoff, and stop for the product owner's next `lanjutkan`.
