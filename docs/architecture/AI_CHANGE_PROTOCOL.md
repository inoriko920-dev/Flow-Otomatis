# ACP-FLOW-OTOMATIS-v1.0

## SEARCH
1. Search exact requested concept and synonyms.
2. Search canonical module owner and relevant port/adapter.
3. Search call sites/imports/event registrations/config references.
4. Read nearest tests/contracts.
5. Read PROJECT_STATE/TASKS/current handoff and inspect baseline/diff.

## UNDERSTAND
1. State current owner/boundary/state/side effects/invariants.
2. Classify request: local bug, feature in existing owner, new external boundary, or genuine new owner.
3. Explain why existing owner is insufficient before creating a new module/service/helper.

## MODIFY
1. Change canonical owner first; do not create parallel path.
2. Keep scope focused.
3. Update tests and source-of-truth docs.
4. Run cheap gates before expensive package/live checks.
5. Review diff for secrets/generated files/cross-layer imports/duplicate helpers/stale docs.
