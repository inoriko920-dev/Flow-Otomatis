# ADR-016 — Generation Request Revision, Fingerprint, and Job Ownership Lease

Status: ACCEPTED FOR A03
Date: 7 October 2026
Scope: STEP 12 audit remediation A03 (F03/F06)

## Context
Queued jobs currently preserve parameters from the first enqueue while later dispatch can read newer scene fields, allowing a request to mix revisions. RUNNING jobs also lack durable owner/lease evidence for safe crash recovery.

## Decision
- Queue preparation freezes one coherent request snapshot with a revision/fingerprint identifying the exact scene inputs used.
- Dispatch validates that the queued revision is still valid and that required inputs remain available through the canonical package/file boundary.
- A changed or unverifiable revision blocks provider dispatch until the user/system explicitly prepares a new coherent request.
- Job ownership is persisted with an owner identity and lease/liveness metadata sufficient to distinguish an active worker from an orphan.
- Orphan recovery moves only proven-orphan work to an attention/recovery state transactionally.
- Ambiguous submit state is never auto-resubmitted.
- Schema migration is versioned, transactional, and preserves historical remote_result_id, result paths, and timestamps.

## Consequences
- A03 requires coordinated port, repository, domain-job, queue-service, and migration changes.
- Legacy jobs without a provable revision are not silently dispatched after migration.
- Two live app instances must not steal an active lease.

## Compatibility
Flow durations remain 4/6/8/10, Audio/SRT Target remains authoritative, and live provider wiring stays blocked.
