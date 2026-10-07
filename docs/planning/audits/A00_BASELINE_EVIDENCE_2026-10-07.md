# A00 Baseline Evidence — 7 October 2026

## Scope
STEP 12 audit-remediation package A00 only. No production source code was modified.

## Repository identity
- Repository: `inoriko920-dev/Flow-Otomatis`
- Branch: `main`
- ASTRA baseline: `e6724a0a5c3d68789149ed5c7eb094d44c9f0967`
- A00 documentation-sync commit tested by CI: `bc550e57407d1be09fceb64eadd18217f4d9c37c`
- Compare result: one commit ahead, documentation files only.

## Official runtime
- GitHub Actions runner: Windows Server 2025
- CPython: 3.14.7 x64
- uv: 0.12.23
- Workflow run: 37639865121
- Quality job: 112855631708
- Job conclusion: SUCCESS

## Commands and results
| Command | Result | Exit / evidence |
|---|---|---|
| `uv sync --frozen --all-groups` | PASS | GitHub Actions step SUCCESS; frozen environment installed |
| `uv run ruff format --check .` | PASS | 123 files already formatted |
| `uv run ruff check .` | PASS | All checks passed |
| `uv run mypy src/flow_otomatis` | PASS | no issues in 63 source files |
| `uv run python scripts/check_architecture.py` | PASS | Architecture check passed |
| `uv run pytest -q tests/unit tests/contract tests/integration tests/smoke tests/ui` | PASS | 90 passed, 1827 warnings in 4.01s |

GitHub Actions marks each command step SUCCESS, which is the official zero-failure/zero-nonzero-exit evidence for this baseline.

## Warning boundary
The 1827 pytest warnings are dominated by the existing PySide6 deprecation warning from `QTableWidgetItem.setTextAlignment(int alignment)`. A00 does not alter that code and does not classify the warning as closure of any F01–F06 finding.

## Finding applicability
Because the A00 tested commit differs from the ASTRA baseline only by documentation, all six audit findings remain applicable:
F01, F02, F03, F04, F05, and F06.

## Gate
A00 PASS:
- source-of-truth audit committed;
- baseline identified and unchanged in code;
- official required runtime available;
- official quality baseline passed;
- ADR decisions required before A01/A03/A04 recorded;
- live Generate remains blocked.
