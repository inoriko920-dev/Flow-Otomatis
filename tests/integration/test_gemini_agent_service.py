from __future__ import annotations

import pytest

from flow_otomatis.application.services.gemini_agent import GeminiAgentService
from flow_otomatis.domain.errors import FlowOtomatisError
from flow_otomatis.domain.gemini import (
    GeminiAgentAction,
    GeminiAgentContext,
    GeminiAgentReply,
)


class FakeKeyService:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    def get_active_secret(self, *, require_valid: bool = True):
        assert require_valid is True
        if self.fail:
            raise FlowOtomatisError("Gemini key aktif harus lolos Cek Health terlebih dahulu.")
        return object(), "secret-fixture-key"


class FakeAgentProvider:
    def __init__(self, reply: GeminiAgentReply) -> None:
        self.reply = reply
        self.calls: list[tuple[str, GeminiAgentContext, str]] = []

    def generate(self, api_key: str, context: GeminiAgentContext, user_message: str):
        self.calls.append((api_key, context, user_message))
        return self.reply


def _context() -> GeminiAgentContext:
    return GeminiAgentContext(
        episode_id="EP_AGENT",
        project_name="Agent Test",
        scene_id="SCENE_001",
        scene_readiness="READY",
        target_duration_s=4.0,
        flow_duration_s=4,
        image_available=True,
    )


def test_agent_requires_manually_selected_healthy_key_before_provider_call() -> None:
    provider = FakeAgentProvider(GeminiAgentReply(message="unused"))
    service = GeminiAgentService(FakeKeyService(fail=True), provider)  # type: ignore[arg-type]

    with pytest.raises(FlowOtomatisError, match="Cek Health"):
        service.ask(_context(), "Apa statusnya?")

    assert provider.calls == []


def test_agent_proposal_never_executes_and_cross_scene_target_is_dropped() -> None:
    provider = FakeAgentProvider(
        GeminiAgentReply(
            message="Sebaiknya tinjau hasil.",
            action=GeminiAgentAction.DOWNLOAD_SCENE,
            target_scene_id="SCENE_999",
            rationale="Fixture",
        )
    )
    service = GeminiAgentService(FakeKeyService(), provider)  # type: ignore[arg-type]

    reply = service.ask(_context(), "  Tolong cek   langkah selanjutnya. ")

    assert len(provider.calls) == 1
    api_key, context, message = provider.calls[0]
    assert api_key == "secret-fixture-key"
    assert context.scene_id == "SCENE_001"
    assert message == "Tolong cek langkah selanjutnya."
    assert reply.action is GeminiAgentAction.NONE
    assert reply.target_scene_id is None
    assert "diabaikan" in reply.rationale
