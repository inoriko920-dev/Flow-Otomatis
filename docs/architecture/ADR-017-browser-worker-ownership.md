# ADR-017 — Browser Worker Ownership and Non-Blocking UI Command Boundary

Status: ACCEPTED FOR A04
Date: 7 October 2026
Scope: STEP 12 audit remediation A04 (F05)

## Context
Current session-check callbacks call synchronous Playwright/CDP work from the Qt UI call path. Browser startup, navigation, and polling can therefore block the event loop.

## Decision
- All Playwright creation, browser/CDP objects, use, and shutdown belong to one dedicated Browser Worker execution owner.
- Qt UI sends commands and receives sanitized DTO/status/error signals; it never owns Playwright page/context/browser objects.
- Duplicate checks for the same profile are rejected or coalesced while busy.
- Startup, connect, navigation, and shutdown each have explicit bounded timeouts.
- Cancellation is cooperative and honest: a button cannot claim to interrupt an already-blocking synchronous Playwright call unless the worker strategy actually supports it.
- UI close/shutdown waits only within a bounded policy and must not transfer browser-object ownership across threads.
- No cookie, token, credential, browser-data content, or sensitive URL is returned through UI DTOs or logs.

## Consequences
- A04 is a process/thread ownership change and must update bootstrap, service command boundary, Browser Worker, and affected UI callback wiring together.
- Slow/failing-driver tests must prove the Qt heartbeat remains responsive.
- Existing normal-Chrome manual authentication lifecycle is preserved.

## Compatibility note
ADR-006's older bundled-Chromium wording is not authority for the manual authentication phase. Current PROJECT_STATE/handoff requires installed normal Chrome for human sign-in, followed by CDP automation only after authentication.
