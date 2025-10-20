"""Service abstraction around ElevenLabs with graceful fallbacks."""
from __future__ import annotations

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Encapsulates ElevenLabs integration with safe fallbacks."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ""
        self._client = None
        if self.api_key:
            try:
                from api.elevenlabs_simple import ElevenLabsSimple  # lazy import
                self._client = ElevenLabsSimple(self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise ElevenLabs client: %s", exc)
                self._client = None

    def generate_audio(self, text: str, voice_id: str = "demo_voice", model_id: str = "eleven_multilingual_v2") -> str:
        """Generate audio with fallback to demo audio."""
        if self._client and text:
            try:
                audio_url = self._client.generate_audio(text, voice_id, model_id)
                if audio_url:
                    return audio_url
            except Exception as exc:
                logger.error("ElevenLabs generation failed: %s", exc)

        # Fallback: demo audio URL
        return "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBun.mp4"

    def list_voices(self) -> List[Dict]:
        """List available voices with fallback to demo voices."""
        if self._client:
            try:
                voices = self._client.get_available_voices()
                if voices:
                    return voices
            except Exception as exc:
                logger.error("ElevenLabs voices fetch failed: %s", exc)

        # Fallback: demo voices
        return [
            {"voice_id": "demo_voice_1", "name": "Демо-голос 1", "category": "male"},
            {"voice_id": "demo_voice_2", "name": "Демо-голос 2", "category": "female"},
            {"voice_id": "demo_voice_3", "name": "Демо-голос 3", "category": "neutral"}
        ]

    def generate_audio_advanced(self, text: str, voice_id: str = "jP9L6ZC55cz5mmx4ZpCk", 
                               model_id: str = "eleven_flash_v2_5",
                               speed: float = 1.0, stability: float = 0.5, 
                               similarity_boost: float = 0.5) -> str:
        """Generate audio with full voice settings and fallback to demo audio."""
        if self._client and text:
            try:
                audio_url = self._client.generate_audio_advanced(
                    text, voice_id, model_id, speed, stability, similarity_boost
                )
                if audio_url:
                    return audio_url
            except Exception as exc:
                logger.error("ElevenLabs advanced generation failed: %s", exc)

        # Fallback: demo audio URL
        return "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBun.mp4"
