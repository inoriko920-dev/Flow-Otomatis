# ADR-015 — Atomic Workspace Create and Explicit Update Semantics

Status: ACCEPTED FOR A01
Date: 7 October 2026
Scope: STEP 12 audit remediation A01 (F01/F02)

## Context
The current repository uses one save path for initial import and later scene updates. Re-importing an existing episode can replace project/scene rows while leaving generation/download records linked by Scene ID, which can surface stale results.

## Decision
- The application persistence port will expose an explicit create operation for a new workspace/project.
- Create must reject an existing episode/project identity atomically at the persistence boundary.
- The current update path used by legitimate scene planning remains an explicit update operation with update semantics.
- A01 will not implement destructive replace, merge, or silent reset of an existing project.
- A duplicate import error is typed and must be translated to a safe Indonesian UI message.
- Missing prompt-reference validation must fail before persistence is called.

## Consequences
- F02 can be closed without deleting old jobs/downloads.
- A future replace/merge feature requires a separate design, migration policy, and destructive confirmation.
- Tests must prove two concurrent creates cannot both succeed.

## Compatibility
No frozen UI redesign is authorized. The UI may only add the minimal duplicate/error state needed by the existing import flow.
