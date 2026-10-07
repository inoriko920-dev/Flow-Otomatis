from __future__ import annotations

from io import BytesIO
from urllib.error import HTTPError

from flow_otomatis.domain.gemini_key import GeminiKeyHealthState
from flow_otomatis.infrastructure.network import gemini_key_health


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb

    def read(self) -> bytes:
        return b'{"models":[]}'


def test_health_probe_uses_header_and_never_generates(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["header"] = request.get_header("X-goog-api-key")
        captured["timeout"] = timeout
        return _Response()

    monkeypatch.setattr(gemini_key_health, "urlopen", fake_urlopen)
    probe = gemini_key_health.GeminiApiKeyHealthProbe(timeout_s=3.5)

    result = probe.check("secret-fixture-key")

    assert result.state is GeminiKeyHealthState.HEALTHY
    assert captured["url"].endswith("/v1beta/models?pageSize=1")
    assert captured["header"] == "secret-fixture-key"
    assert captured["timeout"] == 3.5
    assert "generateContent" not in captured["url"]


def test_health_probe_sanitizes_invalid_key_response(monkeypatch) -> None:
    def fake_urlopen(request, timeout):
        del request, timeout
        raise HTTPError(
            "https://generativelanguage.googleapis.com/v1beta/models",
            403,
            "Forbidden secret-provider-detail",
            {},
            BytesIO(b"secret response body"),
        )

    monkeypatch.setattr(gemini_key_health, "urlopen", fake_urlopen)
    result = gemini_key_health.GeminiApiKeyHealthProbe().check("secret-fixture-key")

    assert result.state is GeminiKeyHealthState.INVALID
    assert "secret" not in result.detail.casefold()
    assert "body" not in result.detail.casefold()
