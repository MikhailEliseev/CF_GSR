"""Service abstraction around AssemblyAI transcription with graceful fallbacks."""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AssemblyService:
    """Encapsulates AssemblyAI transcription with safe fallbacks."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ""
        self._client = None
        if self.api_key:
            try:
                from api.assemblyai_client import AssemblyAIClient  # lazy import
                self._client = AssemblyAIClient(self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise AssemblyAI client: %s", exc)
                self._client = None

    def transcribe(self, video_url: str) -> str:
        """Transcribe video with fallback to demo transcript."""
        if self._client and video_url:
            try:
                transcript = self._client.transcribe_video(video_url)
                if transcript:
                    return transcript
            except Exception as exc:
                logger.error("AssemblyAI transcription failed: %s", exc)

        # Fallback: demo transcript
        return """Демо-транскрипт: Анализ трендов в социальных сетях показывает, что вирусный контент имеет несколько ключевых характеристик. Во-первых, это эмоциональная составляющая - контент должен вызывать сильные чувства. Во-вторых, это актуальность - темы должны быть на пике популярности. В-третьих, это простота восприятия - сложные концепции нужно подавать доступно. Следуя этим принципам, можно создавать контент, который будет набирать миллионы просмотров."""
