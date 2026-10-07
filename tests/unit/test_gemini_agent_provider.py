from __future__ import annotations

import json
from io import BytesIO
from urllib.error import HTTPError

import pytest

from flow_otomatis.application.ports.gemini_agent import GeminiAgentProviderError
from flow_otomatis.domain.gemini import (
    GeminiAgentAction,
    GeminiAgentContext,
)
from flow_otomatis.infrastructure.external import gemini_agent


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def _context() -> GeminiAgentContext:
    return GeminiAgentContext(
        episode_id="EP_AGENT",
        project_name="Agent Test",
        scene_id="SCENE_001",
        scene_readiness="READY",
        target_duration_s=7.2,
        flow_duration_s=8,
        image_available=True,
    )


def test_provider_uses_current_generate_content_contract_without_tools(monkeypatch) -> None:
    captured: dict[str, object] = {}
    structured = {
        "message": "Scene siap.",
        "action": "OPEN_RESULTS",
        "target_scene_id": "",
        "rationale": "Lihat status hasil.",
    }

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["key"] = request.get_header("X-goog-api-key")
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return _Response(
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": json.dumps(structured)}],
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(gemini_agent.urllib.request, "urlopen", fake_urlopen)
    provider = gemini_agent.GeminiGenerateContentAgent(timeout_s=4.5)
    reply = provider.generate("secret-fixture-key", _context(), "Status scene?")

    assert captured["url"].endswith("/models/gemini-3.8-flash:generateContent")
    assert captured["key"] == "secret-fixture-key"
    assert captured["timeout"] == 4.5
    body = captured["body"]
    assert isinstance(body, dict)
    assert "tools" not in body
    assert "secret-fixture-key" not in json.dumps(body)
    assert body["generationConfig"]["responseMimeType"] == "application/json"
    assert reply.action is GeminiAgentAction.OPEN_RESULTS
    assert reply.message == "Scene siap."


def test_provider_sanitizes_rate_limit_and_never_leaks_key(monkeypatch) -> None:
    def fake_urlopen(request, timeout):
        del request, timeout
        raise HTTPError(
            "https://generativelanguage.googleapis.com/v1beta/models/x:generateContent",
            429,
            "secret-provider-detail",
            {},
            BytesIO(b"secret response body"),
        )

    monkeypatch.setattr(gemini_agent.urllib.request, "urlopen", fake_urlopen)
    provider = gemini_agent.GeminiGenerateContentAgent()

    with pytest.raises(GeminiAgentProviderError) as exc_info:
        provider.generate("secret-fixture-key", _context(), "Status?")

    message = str(exc_info.value)
    assert "secret-fixture-key" not in message
    assert "secret-provider-detail" not in message
    assert "diganti otomatis" in message
