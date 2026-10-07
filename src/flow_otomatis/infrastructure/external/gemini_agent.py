"""Text-only Gemini generateContent adapter for the read-only AI Agent."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from flow_otomatis.application.ports.gemini_agent import (
    GeminiAgentProviderError,
    GeminiAgentProviderResult,
)

_DEFAULT_MODEL = "gemini-3.8-flash"
_API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiGenerateContentAgent:
    """Call Gemini without tools, key-in-URL, or provider-side conversation storage."""

    def __init__(
        self,
        *,
        model: str = _DEFAULT_MODEL,
        timeout_s: float = 30.0,
    ) -> None:
        normalized_model = model.strip()
        if not normalized_model or "/" in normalized_model or ":" in normalized_model:
            raise ValueError("Gemini model id is invalid")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self._model = normalized_model
        self._timeout_s = timeout_s

    def ask(
        self,
        *,
        api_key: str,
        system_instruction: str,
        prompt: str,
    ) -> GeminiAgentProviderResult:
        """Generate one answer. This adapter intentionally sends no tools field."""

        url = f"{_API_ROOT}/{self._model}:generateContent"
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_instruction}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 1200,
            },
            "store": False,
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-goog-api-key": api_key,
                "User-Agent": "Flow-Otomatis/0.1",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_s) as response:
                decoded = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in {400, 401, 403}:
                raise GeminiAgentProviderError(
                    "Gemini menolak key atau request AI Agent."
                ) from exc
            if exc.code == 429:
                raise GeminiAgentProviderError(
                    "Gemini sedang membatasi kuota/rate limit. Key tidak diganti otomatis."
                ) from exc
            raise GeminiAgentProviderError(
                f"Gemini AI Agent gagal dengan HTTP {exc.code}."
            ) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise GeminiAgentProviderError(
                "Gemini AI Agent tidak dapat dijangkau."
            ) from exc
        except UnicodeDecodeError, json.JSONDecodeError, TypeError as exc:
            raise GeminiAgentProviderError(
                "Respons Gemini AI Agent tidak dapat diverifikasi."
            ) from exc

        text = self._extract_text(decoded)
        return GeminiAgentProviderResult(text=text, model=self._model)

    @staticmethod
    def _extract_text(payload: object) -> str:
        if not isinstance(payload, dict):
            raise GeminiAgentProviderError("Respons Gemini AI Agent tidak valid.")
        candidates = payload.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise GeminiAgentProviderError("Gemini AI Agent tidak mengembalikan kandidat jawaban.")
        first = candidates[0]
        if not isinstance(first, dict):
            raise GeminiAgentProviderError("Respons kandidat Gemini AI Agent tidak valid.")
        content = first.get("content")
        if not isinstance(content, dict):
            raise GeminiAgentProviderError("Respons Gemini AI Agent tidak memiliki content.")
        parts = content.get("parts")
        if not isinstance(parts, list):
            raise GeminiAgentProviderError("Respons Gemini AI Agent tidak memiliki parts.")
        texts = [
            str(part["text"])
            for part in parts
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ]
        answer = "\n".join(text.strip() for text in texts if text.strip()).strip()
        if not answer:
            raise GeminiAgentProviderError("Gemini AI Agent mengembalikan jawaban kosong.")
        return answer
