"""Generation provider wrapper that enforces the verified Google-session restart gate."""

from __future__ import annotations

from flow_otomatis.application.ports.generation_provider import (
    GenerationAuthenticationRequiredError,
    GenerationProviderPort,
    GenerationProviderResult,
    GenerationRequest,
)
from flow_otomatis.application.services.google_sessions import GoogleSessionService


class RestartGatedGenerationProvider:
    """Block every downstream generation attempt until the selected session gate passes."""

    def __init__(
        self,
        profile_id: str,
        google_sessions: GoogleSessionService,
        downstream: GenerationProviderPort,
    ) -> None:
        self._profile_id = profile_id
        self._google_sessions = google_sessions
        self._downstream = downstream

    def generate(self, request: GenerationRequest) -> GenerationProviderResult:
        """Verify READY-after-restart before allowing any provider mutation."""

        gate = self._google_sessions.get_restart_gate(self._profile_id)
        if not gate.ready_after_restart:
            raise GenerationAuthenticationRequiredError(
                "Profil Google belum lulus Validasi restart. "
                "Pastikan sesi Siap, tutup aplikasi, buka kembali, lalu Cek Ulang Sesi."
            )
        return self._downstream.generate(request)
