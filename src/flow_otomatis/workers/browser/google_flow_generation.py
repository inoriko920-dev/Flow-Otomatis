"""Deterministic Google Flow generation adapter contract for I12-02A.

No live selectors or Google Flow mutation are implemented in this module yet.
It defines the Browser Worker seam and maps controlled driver evidence into the
provider-neutral queue contract, including ambiguous-submit protection.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from flow_otomatis.application.ports.generation_provider import (
    GenerationAuthenticationRequiredError,
    GenerationCancelledError,
    GenerationProviderError,
    GenerationProviderResult,
    GenerationRequest,
    GenerationSubmissionAmbiguousError,
)
from flow_otomatis.workers.browser.google_flow_request_plan import (
    prepare_google_flow_request,
)


class GoogleFlowSubmitState(StrEnum):
    """Sanitized one-submit outcome emitted by a Browser Worker driver."""

    ACCEPTED = "ACCEPTED"
    SAFE_FAILURE = "SAFE_FAILURE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    CANCELLED = "CANCELLED"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True, slots=True)
class GoogleFlowSubmitEvidence:
    """Credential-free evidence from exactly one submit attempt."""

    state: GoogleFlowSubmitState
    detail: str
    remote_result_id: str | None = None


class GoogleFlowGenerationDriver(Protocol):
    """Browser-owned driver seam; the live Playwright implementation comes later."""

    def submit_one(
        self,
        profile_id: str,
        request: GenerationRequest,
        *,
        timeout_ms: int,
    ) -> GoogleFlowSubmitEvidence:
        """Attempt at most one provider mutation and classify its outcome."""


class GoogleFlowGenerationProvider:
    """Map one deterministic Browser Worker attempt into queue-safe semantics."""

    def __init__(
        self,
        profile_id: str,
        driver: GoogleFlowGenerationDriver,
        *,
        timeout_ms: int = 120_000,
    ) -> None:
        if timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")
        self._profile_id = profile_id
        self._driver = driver
        self._timeout_ms = timeout_ms

    def generate(self, request: GenerationRequest) -> GenerationProviderResult:
        """Perform exactly one driver attempt; never auto-retry a mutation."""

        prepare_google_flow_request(request)
        evidence = self._driver.submit_one(
            self._profile_id,
            request,
            timeout_ms=self._timeout_ms,
        )
        detail = evidence.detail[:500]

        if evidence.state is GoogleFlowSubmitState.ACCEPTED:
            remote_result_id = (evidence.remote_result_id or "").strip()
            if not remote_result_id:
                raise GenerationSubmissionAmbiguousError(
                    "Flow reported acceptance without a stable result identifier."
                )
            return GenerationProviderResult(remote_result_id=remote_result_id)

        if evidence.state is GoogleFlowSubmitState.AMBIGUOUS:
            raise GenerationSubmissionAmbiguousError(detail or "Flow submit outcome is ambiguous.")

        if evidence.state is GoogleFlowSubmitState.AUTH_REQUIRED:
            raise GenerationAuthenticationRequiredError(
                detail or "Google session requires manual login."
            )

        if evidence.state is GoogleFlowSubmitState.CANCELLED:
            raise GenerationCancelledError(detail or "Generation was cancelled safely.")

        raise GenerationProviderError(detail or "Google Flow rejected the generation request.")
