"""Review-only Gemini AI Agent orchestration."""

from __future__ import annotations

from flow_otomatis.application.ports.gemini_agent import (
    GeminiAgentProviderError,
    GeminiAgentProviderPort,
)
from flow_otomatis.application.services.gemini_keys import GeminiKeyService
from flow_otomatis.domain.errors import FlowOtomatisError
from flow_otomatis.domain.gemini import (
    GeminiAgentAction,
    GeminiAgentContext,
    GeminiAgentReply,
)


class GeminiAgentService:
    """Ask Gemini with the manually selected healthy key and safe local context."""

    def __init__(
        self,
        key_service: GeminiKeyService,
        provider: GeminiAgentProviderPort,
    ) -> None:
        self._key_service = key_service
        self._provider = provider

    def ask(
        self,
        context: GeminiAgentContext,
        user_message: str,
    ) -> GeminiAgentReply:
        """Return advisory text; never execute the returned action proposal."""

        message = " ".join(user_message.split())
        if not message:
            raise FlowOtomatisError("Pesan untuk AI Agent tidak boleh kosong.")
        if len(message) > 4000:
            raise FlowOtomatisError("Pesan AI Agent maksimal 4000 karakter.")

        _profile, secret = self._key_service.get_active_secret(require_valid=True)
        try:
            reply = self._provider.generate(secret, context, message)
        except GeminiAgentProviderError as exc:
            raise FlowOtomatisError(str(exc)) from exc

        clean_message = reply.message.strip()
        if not clean_message:
            raise FlowOtomatisError("Gemini tidak mengembalikan jawaban yang dapat digunakan.")

        action = reply.action
        target = reply.target_scene_id
        rationale = reply.rationale.strip()[:500]
        if action in {GeminiAgentAction.REVIEW_SCENE, GeminiAgentAction.DOWNLOAD_SCENE}:
            if target not in {None, "", context.scene_id}:
                action = GeminiAgentAction.NONE
                target = None
                rationale = "Usulan lintas Scene diabaikan demi menjaga scope Scene aktif."
            else:
                target = context.scene_id

        return GeminiAgentReply(
            message=clean_message[:4000],
            action=action,
            target_scene_id=target,
            rationale=rationale,
        )
