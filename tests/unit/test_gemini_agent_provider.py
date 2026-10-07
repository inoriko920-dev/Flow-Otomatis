from __future__ import annotations

import io
import json
import urllib.error

import pytest

from flow_otomatis.application.ports.gemini_agent import GeminiAgentProviderError
from flow_otomatis.infrastructure.external.gemini_agent import GeminiGenerateContentAgent


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        del exc_type, exc, tb

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def test_agent_uses_header_no_tools_and_no_provider_storage(monkeypatch) -> None:
    raw_key = "secret-agent-key-" + "X" * 24
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["key"] = request.get_header("X-goog-api-key")
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "Jawaban fixture yang aman."}],
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    provider = GeminiGenerateContentAgent(timeout_s=4)
    result = provider.ask(
        api_key=raw_key,
        system_instruction="Read-only system.",
        prompt="Apa status scene?",
    )

    assert result.model == "gemini-3.8-flash"
    assert result.text == "Jawaban fixture yang aman."
    assert raw_key not in str(captured["url"])
    assert captured["key"] == raw_key
    body = captured["body"]
    assert isinstance(body, dict)
    assert "tools" not in body
    assert body["store"] is False
    assert raw_key not in json.dumps(body)
    assert captured["timeout"] == 4


def test_agent_rate_limit_is_sanitized_and_not_retried(monkeypatch) -> None:
    calls = 0

    def fake_urlopen(request, timeout):
        nonlocal calls
        del request, timeout
        calls += 1
        raise urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash",
            code=429,
            msg="secret provider detail",
            hdrs=None,
            fp=io.BytesIO(b'{"secret":"do not expose"}'),
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(GeminiAgentProviderError, match="tidak diganti otomatis") as caught:
        GeminiGenerateContentAgent().ask(
            api_key="secret-agent-key",
            system_instruction="Read-only.",
            prompt="Status?",
        )

    assert calls == 1
    assert "secret" not in str(caught.value).casefold()
