"""Service-level wrapper for OpenAI assistants with safe fallbacks."""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OpenAIService:
    """Provides high-level helpers for OpenAI-powered flows."""

    def __init__(self, api_key: str | None = None):
        self.api_key = (api_key or "").strip()
        self._client = None
        if self.api_key:
            try:
                from api.openai_client import OpenAIClient

                self._client = OpenAIClient(self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise OpenAI client: %s", exc)
                self._client = None

    @property
    def client(self):  # pragma: no cover - convenience for legacy code
        return self._client

    def test_connection(self, assistant_id: Optional[str] = None) -> bool:
        if not self._client or not assistant_id:
            return False
        try:
            return self._client.test_connection(assistant_id)
        except Exception as exc:
            logger.error("OpenAI test connection failed: %s", exc)
            return False

    def generate_with_assistant(self, assistant_id: str, master_prompt: str, context: str) -> str:
        """Generate text via assistant, fallback to canned script."""
        if self._client and assistant_id:
            try:
                return self._client.generate_text_for_video(assistant_id, master_prompt, context)
            except Exception as exc:
                logger.error("OpenAI assistant generation failed: %s", exc)

        logger.info("Using fallback OpenAI generation")
        return (
            "Привет! Это демонстрационный текст, созданный когда OpenAI недоступен. "
            "Добавьте сюда свою идею и продолжайте работать, сервис восстановится автоматически."
        )

    def rewrite_transcript(self, transcript: str, master_prompt: Optional[str] = None) -> str:
        """Rewrite transcript using chat completion, fallback otherwise."""
        user_prompt = (
            master_prompt or
            "Сделай текст динамичным, добавь эмоции, структуру и призыв к действию."
        )
        combined_prompt = f"{user_prompt}\n\nИсходный текст:\n{transcript}"

        if self._client:
            try:
                return self._client._chat_completion([
                    {"role": "user", "content": combined_prompt}
                ])
            except Exception as exc:
                logger.error("OpenAI rewrite failed: %s", exc)

        return (
            "🔥 Демо-версия переписанного текста. Добавьте свои правки, "
            "пока OpenAI недоступен."
        )

    def create_assistant_message(self, assistant_id: str, prompt: str):
        """Small helper mirroring legacy behaviour."""
        if self._client and assistant_id:
            try:
                return self._client.create_assistant_message(assistant_id, prompt)
            except Exception as exc:
                logger.error("OpenAI assistant message failed: %s", exc)
        return {"content": self.generate_with_assistant(assistant_id, "", prompt)}
