"""Service wrapper for AssemblyAI with optional fallback."""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AssemblyService:
    """Transcription service backed by AssemblyAI."""

    def __init__(self, api_key: str | None = None):
        self.api_key = (api_key or "").strip()
        self._client = None
        if self.api_key:
            try:
                from api.assemblyai_client_improved import AssemblyAIClientImproved

                self._client = AssemblyAIClientImproved(self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise AssemblyAI client: %s", exc)
                self._client = None

    def transcribe(self, audio_url: str) -> str:
        """Transcribe remote audio, return fallback text on failure."""
        if not audio_url:
            raise ValueError("audio_url must be provided")

        if self._client:
            try:
                if not self._client.test_connection():
                    logger.error("AssemblyAI connection test failed")
                else:
                    transcript = self._client.transcribe_audio_url(audio_url)
                    if transcript:
                        return transcript
            except Exception as exc:
                logger.error("AssemblyAI transcription failed: %s", exc)

        logger.info("Using fallback transcript for %s", audio_url)
        return (
            "Демо транскрипт: сервис AssemblyAI недоступен, поэтому используется "
            "пример текста для дальнейшего шага."
        )
