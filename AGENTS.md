# AGENTS.md — Flow-Otomatis

## Identity
Flow-Otomatis is a Windows 11 x64 desktop application distributed as a portable ZIP. Primary UI language: Indonesian.

## Read before changing anything
1. PROJECT_STATE.md
2. TASKS.md
3. docs/planning/
4. docs/ui/
5. docs/architecture/
6. docs/adr/
7. docs/handoff/current/

## Architecture
presentation -> application -> domain
infrastructure -> application ports/domain/contracts
workers/browser -> contracts + flow_web internals
bootstrap -> composition only

## Search before create
Before adding a file/class/service/helper:
- search exact concept + synonyms;
- search canonical owner, ports/interfaces, tests, config, call-sites/imports;
- read nearest tests/contracts;
- state why existing canonical owner is insufficient.

## Forbidden
- secrets/session/cookie/token in repo/log/docs/fixtures;
- hard-coded C:\ or D:\ paths or CWD dependence;
- presentation importing infrastructure/provider/browser/sqlite/keyring;
- direct Playwright outside browser worker/flow_web;
- generic utils.py/helpers2.py/Manager dumping grounds;
- hidden mutable global state;
- force reset/overwrite unknown work;
- generated build/cache/user-data commits;
- claiming tests/live provider behavior that were not run;
- production coding while PROJECT_STATE says documentation gate BLOCKED.

## Planned canonical commands
- uv sync --frozen
- uv run ruff format --check .
- uv run ruff check .
- uv run mypy src/flow_otomatis
- uv run python scripts/check_architecture.py
- uv run pytest -q tests/unit tests/contract

## Change protocol
BEFORE: verify branch/SHA/diff, identify canonical owner/tests.
DURING: keep scope focused, preserve frozen product/UI, update tests with behavior.
AFTER: run gates, review diff, update TASKS.md/PROJECT_STATE.md, record evidence.

## Astra review triggers
Stop affected work for cross-module contract/schema/migration/core dependency/security boundary/process model/UI freeze/provider-policy changes.

## Portable contract
Use canonical PathService. LocalAppData owns app/session/log/cache state. Projects are user-selectable. Never rely on shell CWD.
