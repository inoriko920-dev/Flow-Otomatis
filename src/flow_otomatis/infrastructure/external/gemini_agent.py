"""Gemini generateContent adapter for the review-only AI Agent."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from flow_otomatis.application.ports.gemini_agent import GeminiAgentProviderError
from flow_otomatis.domain.gemini import (
    GeminiAgentAction,
    GeminiAgentContext,
    GeminiAgentReply,
)

_DEFAULT_MODEL = "gemini-3.8-flash"
_API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"

_SYSTEM_INSTRUCTION = """You are the advisory AI Agent inside Flow-Otomatis.
Answer in concise Indonesian. You may explain local project/Scene state and propose a safe next
step, but you MUST NOT claim that you executed anything. Never ask for passwords, MFA codes,
cookies, browser profiles, or API keys. Never propose automatic account/key rotation or quota
evasion. Never propose a blind retry of Generate after an ambiguous provider outcome.
Allowed action proposals are only NONE, REVIEW_SCENE, OPEN_RESULTS, OPEN_GOOGLE_PROFILES,
or DOWNLOAD_SCENE. A proposal is review-only and the desktop app will not execute it
automatically.
"""


class GeminiGenerateContentAgent:
    """Call Gemini with structured JSON output and no executable tools/functions."""

    def __init__(
        self,
        *,
        model: str = _DEFAULT_MODEL,
        timeout_s: float = 30.0,
    ) -> None:
        normalized_model = model.strip().removeprefix("models/")
        if not normalized_model:
            raise ValueError("model must not be empty")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self._model = normalized_model
        self._timeout_s = timeout_s

    @property
    def model(self) -> str:
        return self._model

    def generate(
        self,
        api_key: str,
        context: GeminiAgentContext,
        user_message: str,
    ) -> GeminiAgentReply:
        model = urllib.parse.quote(self._model, safe="-._")
        url = f"{_API_ROOT}/{model}:generateContent"
        payload = {
            "systemInstruction": {"parts": [{"text": _SYSTEM_INSTRUCTION}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "episode_id": context.episode_id,
                                    "project_name": context.project_name,
                                    "scene_id": context.scene_id,
                                    "scene_readiness": context.scene_readiness,
                                    "target_duration_s": context.target_duration_s,
                                    "flow_duration_s": context.flow_duration_s,
                                    "image_available": context.image_available,
                                    "user_message": user_message,
                                },
                                ensure_ascii=False,
                                separators=(",", ":"),
                            )
                        }
                    ],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "message": {"type": "STRING"},
                        "action": {
                            "type": "STRING",
                            "enum": [item.value for item in GeminiAgentAction],
                        },
                        "target_scene_id": {"type": "STRING"},
                        "rationale": {"type": "STRING"},
                    },
                    "required": ["message", "action", "rationale"],
                },
                "candidateCount": 1,
                "maxOutputTokens": 700,
                "temperature": 0.2,
            },
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Flow-Otomatis/0.1",
                "x-goog-api-key": api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self._timeout_s) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in {400, 401, 403}:
                raise GeminiAgentProviderError(
                    "Gemini menolak request atau key aktif. Jalankan Cek Health terlebih dahulu."
                ) from exc
            if exc.code == 429:
                raise GeminiAgentProviderError(
                    "Gemini sedang membatasi request/kuota. Key aktif tidak diganti otomatis."
                ) from exc
            raise GeminiAgentProviderError(
                f"Gemini AI Agent gagal dengan HTTP {exc.code}."
            ) from exc
        except urllib.error.URLError, TimeoutError, OSError as exc:
            raise GeminiAgentProviderError(
                "Gemini AI Agent tidak dapat dijangkau. Coba lagi setelah koneksi stabil."
            ) from exc
        except UnicodeDecodeError, json.JSONDecodeError, TypeError as exc:
            raise GeminiAgentProviderError(
                "Respons Gemini AI Agent tidak dapat diverifikasi."
            ) from exc

        text = self._extract_text(response_payload)
        try:
            structured = json.loads(text)
        except (json.JSONDecodeError, TypeError) as exc:
            raise GeminiAgentProviderError(
                "Gemini mengembalikan respons yang tidak sesuai format AI Agent."
            ) from exc
        if not isinstance(structured, dict):
            raise GeminiAgentProviderError("Format respons Gemini AI Agent tidak valid.")

        message = structured.get("message")
        action_raw = structured.get("action", GeminiAgentAction.NONE.value)
        rationale = structured.get("rationale", "")
        target = structured.get("target_scene_id")
        if not isinstance(message, str) or not isinstance(rationale, str):
            raise GeminiAgentProviderError("Field respons Gemini AI Agent tidak valid.")

        try:
            action = GeminiAgentAction(str(action_raw))
        except ValueError:
            action = GeminiAgentAction.NONE

        return GeminiAgentReply(
            message=message,
            action=action,
            target_scene_id=str(target) if isinstance(target, str) and target.strip() else None,
            rationale=rationale,
        )

    @staticmethod
    def _extract_text(payload: object) -> str:
        if not isinstance(payload, dict):
            raise GeminiAgentProviderError("Respons Gemini AI Agent tidak memiliki kandidat.")
        candidates = payload.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise GeminiAgentProviderError("Gemini AI Agent tidak mengembalikan kandidat.")
        first = candidates[0]
        if not isinstance(first, dict):
            raise GeminiAgentProviderError("Kandidat Gemini AI Agent tidak valid.")
        content = first.get("content")
        if not isinstance(content, dict):
            raise GeminiAgentProviderError("Konten Gemini AI Agent tidak tersedia.")
        parts = content.get("parts")
        if not isinstance(parts, list):
            raise GeminiAgentProviderError("Bagian respons Gemini AI Agent tidak tersedia.")
        texts = [
            part.get("text")
            for part in parts
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ]
        result = "".join(texts).strip()
        if not result:
            raise GeminiAgentProviderError("Gemini AI Agent mengembalikan respons kosong.")
        return result
