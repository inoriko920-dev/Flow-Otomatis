from __future__ import annotations

import io
import urllib.error

from flow_otomatis.domain.gemini import GeminiKeyStatus
from flow_otomatis.infrastructure.external.gemini_health import GeminiModelsHealthChecker


class FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        del exc_type, exc, tb

    def read(self) -> bytes:
        return self._payload


def test_health_checker_uses_header_not_query_string(monkeypatch) -> None:
    raw_key = "secret-auth-key-" + "X" * 24
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["key"] = request.get_header("X-goog-api-key")
        captured["timeout"] = timeout
        return FakeResponse(b'{"models":[{"name":"models/gemini-fixture"}]}')

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = GeminiModelsHealthChecker(timeout_s=3).check(raw_key)

    assert result.status is GeminiKeyStatus.VALID
    assert raw_key not in str(captured["url"])
    assert captured["key"] == raw_key
    assert captured["timeout"] == 3


def test_health_checker_returns_sanitized_invalid_status(monkeypatch) -> None:
    raw_key = "secret-auth-key-" + "Y" * 24

    def fake_urlopen(request, timeout):
        del request, timeout
        raise urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com/v1beta/models",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"do not surface body"}'),
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = GeminiModelsHealthChecker().check(raw_key)

    assert result.status is GeminiKeyStatus.INVALID
    assert raw_key not in result.detail
    assert "auth key" in result.detail
