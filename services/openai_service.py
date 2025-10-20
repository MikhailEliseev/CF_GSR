"""Service abstraction around OpenAI with graceful fallbacks."""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OpenAIService:
    """Encapsulates OpenAI integration with safe fallbacks."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ""
        self._client = None
        if self.api_key:
            try:
                from api.openai_client import OpenAIClient  # lazy import
                self._client = OpenAIClient(self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise OpenAI client: %s", exc)
                self._client = None

    def rewrite_transcript(self, transcript: str, master_prompt: str = "") -> str:
        """Rewrite transcript with fallback to demo text."""
        if self._client and transcript:
            try:
                rewritten = self._client.rewrite_text(transcript, master_prompt)
                if rewritten:
                    return rewritten
            except Exception as exc:
                logger.error("OpenAI rewrite failed: %s", exc)

        # Fallback: demo rewritten text
        return f"""Переписанный текст на основе анализа трендов:

{transcript[:100]}...

Ключевые тренды этого сезона включают в себя:
1. Эмоциональная связь с аудиторией
2. Актуальные темы и проблемы
3. Простота и понятность подачи
4. Визуальная привлекательность

Следуя этим принципам, можно создавать контент, который будет резонировать с широкой аудиторией и набирать вирусные просмотры."""

    def generate_text(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Генерация текста через OpenAI с fallback"""
        if self._client:
            try:
                messages = [
                    {"role": "user", "content": prompt}
                ]
                return self._client._chat_completion(messages)
            except Exception as exc:
                logger.error("OpenAI generate_text failed: %s", exc)
        
        # Fallback: возвращаем часть промпта
        return "Текст сгенерирован в демо-режиме. Настройте OpenAI API ключ для полной функциональности."
