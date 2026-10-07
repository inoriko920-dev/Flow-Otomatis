"""Read-only Gemini API-key health probe."""

from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flow_otomatis.domain.gemini_key import GeminiKeyHealthResult, GeminiKeyHealthState

_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1"


class GeminiApiKeyHealthProbe:
    """Validate authentication with models.list; never generate content."""

    def __init__(self, *, timeout_s: float = 8.0) -> None:
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self._timeout_s = timeout_s

    def check(self, api_key: str) -> GeminiKeyHealthResult:
        request = Request(
            _MODELS_URL,
            headers={
                "Accept": "application/json",
                "x-goog-api-key": api_key,
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=self._timeout_s) as response:
                status = int(response.status)
        except HTTPError as exc:
            if exc.code in {400, 401, 403}:
                return GeminiKeyHealthResult(
                    GeminiKeyHealthState.INVALID,
                    "Key ditolak oleh Gemini API.",
                )
            if exc.code == 429:
                return GeminiKeyHealthResult(
                    GeminiKeyHealthState.RATE_LIMITED,
                    "Key dikenali, tetapi layanan sedang membatasi permintaan.",
                )
            return GeminiKeyHealthResult(
                GeminiKeyHealthState.ERROR,
                f"Gemini API mengembalikan HTTP {exc.code}.",
            )
        except (URLError, TimeoutError, OSError):
            return GeminiKeyHealthResult(
                GeminiKeyHealthState.ERROR,
                "Gemini API tidak dapat dijangkau untuk health check.",
            )

        if 200 <= status < 300:
            return GeminiKeyHealthResult(
                GeminiKeyHealthState.HEALTHY,
                "Key diterima oleh Gemini API.",
            )
        return GeminiKeyHealthResult(
            GeminiKeyHealthState.ERROR,
            f"Gemini API mengembalikan status HTTP {status}.",
        )
