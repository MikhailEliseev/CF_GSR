"""Wrapper around ElevenLabs with fallbacks for offline mode."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_DEMO_AUDIO = "https://file-examples.com/storage/fe9fd5da4b3ebabb00df5b9/2017/11/file_example_MP3_700KB.mp3"


class ElevenLabsService:
    """Speech synthesis helper with optional fallbacks."""

    def __init__(self, api_key: str | None = None):
        self.api_key = (api_key or "").strip()
        self._client = None
        if self.api_key:
            try:
                from api.elevenlabs_simple import ElevenLabsSimple

                self._client = ElevenLabsSimple(self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise ElevenLabs client: %s", exc)
                self._client = None
        else:
            try:
                from api.elevenlabs_simple import ElevenLabsSimple

                self._client = ElevenLabsSimple()
            except Exception:
                self._client = None

    def list_voices(self) -> List[Dict]:
        """Return available voices or defaults."""
        if self._client:
            try:
                voices = self._client.get_available_voices()
                if voices:
                    return voices
            except Exception as exc:
                logger.error("ElevenLabs voices fetch failed: %s", exc)
        return [
            {
                "voice_id": "demo_voice",
                "name": "Demo Voice",
                "category": "premade",
                "description": "Используется пока ElevenLabs недоступен",
            }
        ]

    def generate_audio(self, text: str, voice_id: Optional[str] = None, model_id: Optional[str] = None) -> str:
        """Generate audio from text or fallback to demo file."""
        if not text:
            raise ValueError("text must be provided")

        if self._client:
            try:
                audio_url = self._client.generate_audio(text, voice_id=voice_id, model_id=model_id)
                if audio_url:
                    return audio_url
            except Exception as exc:
                logger.error("ElevenLabs generation failed: %s", exc)

        logger.info("Using fallback ElevenLabs audio")
        return _DEMO_AUDIO
    def test_connection(self) -> bool:
        if self._client:
            try:
                return bool(getattr(self._client, 'test_connection', lambda: True)())
            except Exception:
                return False
        return False

    def generate_speech_for_video(self, text: str, voice_id: Optional[str] = None, model_id: Optional[str] = None) -> str:
        return self.generate_audio(text, voice_id=voice_id, model_id=model_id)

