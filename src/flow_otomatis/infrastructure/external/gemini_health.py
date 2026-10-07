"""Official Gemini API health check using a header-only API key."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from flow_otomatis.application.ports.gemini_keys import GeminiKeyHealthEvidence
from flow_otomatis.domain.gemini import GeminiKeyStatus

_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1"


class GeminiModelsHealthChecker:
    """Validate a key by listing one available Gemini model."""

    def __init__(self, *, timeout_s: float = 8.0) -> None:
        self._timeout_s = max(timeout_s, 1.0)

    def check(self, api_key: str) -> GeminiKeyHealthEvidence:
        request = urllib.request.Request(
            _MODELS_URL,
            headers={
                "x-goog-api-key": api_key,
                "Accept": "application/json",
                "User-Agent": "Flow-Otomatis/0.1",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in {400, 401, 403}:
                return GeminiKeyHealthEvidence(
                    status=GeminiKeyStatus.INVALID,
                    detail="Gemini API menolak key. Gunakan auth key AI Studio yang masih berlaku.",
                )
            if exc.code == 429:
                return GeminiKeyHealthEvidence(
                    status=GeminiKeyStatus.ERROR,
                    detail="Gemini API membatasi request/kuota saat health check.",
                )
            return GeminiKeyHealthEvidence(
                status=GeminiKeyStatus.ERROR,
                detail=f"Gemini API health check gagal dengan HTTP {exc.code}.",
            )
        except urllib.error.URLError, TimeoutError, OSError:
            return GeminiKeyHealthEvidence(
                status=GeminiKeyStatus.ERROR,
                detail="Gemini API tidak dapat dijangkau saat health check.",
            )
        except UnicodeDecodeError, json.JSONDecodeError, TypeError:
            return GeminiKeyHealthEvidence(
                status=GeminiKeyStatus.ERROR,
                detail="Respons Gemini API tidak dapat diverifikasi.",
            )

        if isinstance(payload, dict) and isinstance(payload.get("models"), list):
            return GeminiKeyHealthEvidence(
                status=GeminiKeyStatus.VALID,
                detail="Gemini API key valid dan endpoint models dapat diakses.",
            )
        return GeminiKeyHealthEvidence(
            status=GeminiKeyStatus.ERROR,
            detail="Respons Gemini API tidak memuat daftar model yang diharapkan.",
        )
