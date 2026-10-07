# STEP 08 BLOCKER — B08-DOCBIN-001

## Status
BLOCKING PRODUCTION CODING.

## Problem
The connected GitHub writer available in this session supports UTF-8 text file creation/update but exposes no direct binary DOCX/PNG upload action. The project owner's rule requires every planning DOCX and Final UI Reference asset to be physically present in the repository before coding.

## Work completed
- repository initialized;
- governance text committed;
- architecture/code constitution committed;
- documentation/UI binary manifests with SHA-256 committed;
- Software Factory guide added to required source-of-truth manifest;
- no `src/` or production code created;
- repo-ready binary source-of-truth pack prepared and integrity-tested.

## Prepared transfer pack
- `Flow-Otomatis_S08_T01_BINARY_SOURCE_OF_TRUTH_UPLOAD_PACK.zip`
- Size: 83847809 bytes
- SHA-256: `7f14ee5a877d041daa08a486628f8541d62fe1ecffdd20cd8b2230a28b56f107`
- 47 entries
- ZIP integrity: PASS

The pack already uses the final repository-relative paths. It is only a transfer aid; committing the ZIP itself does NOT satisfy the gate unless its files are extracted into the canonical paths and verified.

## Still required
Upload and hash-verify every PENDING binary in:
- `docs/planning/SOURCE_OF_TRUTH_MANIFEST.md`
- `docs/ui/UI_REFERENCE_MANIFEST.md`

## Gate
Do not start S08-T02 until this blocker is cleared. Do not weaken the gate merely because text summaries or the upload pack exist.
