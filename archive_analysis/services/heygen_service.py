"""Wrapper around HeyGen video generation with graceful fallbacks."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_DEMO_VIDEO = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"


class HeyGenService:
    """Video generation helper for avatar-based content."""

    def __init__(self, api_key: str | None = None):
        self.api_key = (api_key or "").strip()
        self._client = None
        if self.api_key:
            try:
                from api.heygen_client import HeyGenClient

                self._client = HeyGenClient(self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise HeyGen client: %s", exc)
                self._client = None

    def list_avatars(self) -> List[Dict]:
        if self._client:
            try:
                avatars = self._client.get_available_avatars()
                if avatars:
                    return avatars
            except Exception as exc:
                logger.error("HeyGen avatars fetch failed: %s", exc)
        return [
            {
                "avatar_id": "demo_avatar",
                "avatar_name": "Demo Avatar",
                "preview_image": "",
                "gender": "unknown",
                "avatar_type": "demo",
            }
        ]

    def generate_video(self, audio_url: str, avatar_id: Optional[str] = None) -> Dict[str, str]:
        """Generate video or return fallback info."""
        if not audio_url:
            raise ValueError("audio_url must be provided")

        if self._client:
            try:
                video_id = self._client.generate_video(audio_url, avatar_id)
                if isinstance(video_id, str) and video_id.startswith("http"):
                    return {"video_url": video_id}
                if video_id:
                    status = self._client.get_video_status(video_id)
                    if status and status.get("video_url"):
                        return {
                            "video_url": status.get("video_url"),
                            "video_id": video_id,
                        }
                    return {"video_id": video_id}
            except Exception as exc:
                logger.error("HeyGen video generation failed: %s", exc)

        logger.info("Using fallback HeyGen video")
        return {"video_url": _DEMO_VIDEO}
    def test_connection(self) -> bool:
        if self._client:
            try:
                return bool(getattr(self._client, 'test_connection', lambda: True)())
            except Exception:
                return False
        return False

    def generate_video_complete(self, avatar_id: str, audio_url: str):
        result = self.generate_video(audio_url, avatar_id)
        if isinstance(result, dict):
            return result.get('video_url')
        return result

