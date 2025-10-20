"""Service abstraction around HeyGen with graceful fallbacks."""
from __future__ import annotations

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class HeyGenService:
    """Encapsulates HeyGen integration with safe fallbacks."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ""
        self._client = None
        if self.api_key:
            try:
                from api.heygen_client import HeyGenClient  # lazy import
                self._client = HeyGenClient(self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise HeyGen client: %s", exc)
                self._client = None

    def generate_video(self, audio_url: str, avatar_id: str = "demo_avatar") -> Dict:
        """Generate video with fallback to demo video."""
        if self._client and audio_url:
            try:
                video_info = self._client.create_video(audio_url, avatar_id)
                if video_info:
                    return video_info
            except Exception as exc:
                logger.error("HeyGen generation failed: %s", exc)

        # Fallback: demo video info
        return {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBun.mp4",
            "video_id": "demo_video_123",
            "status": "completed",
            "duration": 40
        }

    def list_avatars(self) -> List[Dict]:
        """List available avatars with fallback to demo avatars."""
        if self._client:
            try:
                avatars = self._client.get_available_avatars()
                if avatars:
                    return avatars
            except Exception as exc:
                logger.error("HeyGen avatars fetch failed: %s", exc)

        # Fallback: demo avatars
        return [
            {"avatar_id": "demo_avatar_1", "name": "Демо-аватар 1", "gender": "male"},
            {"avatar_id": "demo_avatar_2", "name": "Демо-аватар 2", "gender": "female"},
            {"avatar_id": "demo_avatar_3", "name": "Демо-аватар 3", "gender": "neutral"}
        ]
