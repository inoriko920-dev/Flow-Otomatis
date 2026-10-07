# CC-FLOW-OTOMATIS-v1.0

## Hard principles
- Search -> Understand -> Modify.
- Single canonical owner for each concern.
- Thin entry points; no hidden global state.
- Explicit contracts and typed errors.
- Portable path/resource resolution.
- UI never calls filesystem/DB/network/browser/provider directly.
- Domain does not depend on Qt/Playwright/sqlite/keyring.
- External mutations are stage/idempotency aware.
- No secrets in repo/project/log/diagnostic export.
- Evidence beats assumption.

## Dependency direction
presentation -> application -> domain
application -> contracts/ports
infrastructure -> application ports/domain/contracts
workers/browser -> contracts + flow_web internals
bootstrap -> wires concrete implementations

## Mandatory AI protocol
SEARCH -> UNDERSTAND -> MODIFY before creating helpers/services/modules. Search synonyms, canonical owner, call sites, tests, config and contracts first.
