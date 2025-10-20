"""Service abstraction around Apify Instagram scraping with graceful fallbacks."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)


class ApifyService:
    """Encapsulates Apify Instagram scraping with safe fallbacks."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ""
        self._client = None
        if self.api_key:
            try:
                from api.apify_client import ApifyInstagramClient  # lazy import

                self._client = ApifyInstagramClient(self.api_key)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Failed to initialise Apify client: %s", exc)
                self._client = None

    def fetch_reels(self, competitors: List[str], count: int) -> List[Dict]:
        """Fetch reels for competitors, falling back to demo data if needed."""
        if count <= 0:
            return []

        if self._client and competitors:
            try:
                reels = self._client.get_trending_content(competitors, days_back=7)
                if reels:
                    return reels[:count]
            except Exception as exc:  # pragma: no cover - network issues
                logger.error("Apify request failed: %s", exc)

        # Fallback: fabricate minimal demo reels so UI keeps functioning
        fallback: List[Dict] = []
        now = datetime.utcnow()
        for idx, competitor in enumerate(competitors or ["demo_account"]):
            for reel_index in range(min(count, 3)):
                fallback.append(
                    {
                        "id": str(uuid.uuid4()),
                        "source_username": competitor,
                        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                        "thumbnail_url": "https://dummyimage.com/400x700/1f7a1f/ffffff.png&text=Demo+Reel",
                        "caption": "Демо-контент для отладки Apify",
                        "hashtags": ["demo", "content", "gsr"],
                        "views_count": 35000 + 5000 * reel_index,
                        "likes_count": 1200 + 200 * reel_index,
                        "comments_count": 150 + 10 * reel_index,
                        "engagement_rate": 0.12,
                        "is_viral": True,
                        "timestamp": (now - timedelta(hours=idx * 4 + reel_index)).isoformat(),
                        "music": "Demo Track",
                        "first_comment": "Это лишь демонстрация.",
                    }
                )
        return fallback[:count]

    def test_connection(self) -> bool:
        if self._client:
            try:
                return bool(getattr(self._client, 'test_connection', lambda: True)())
            except Exception:
                return False
        return False

    def get_trending_content(self, competitors: List[str], days_back: int = 7) -> List[Dict]:
        if self._client and competitors:
            try:
                return self._client.get_trending_content(competitors, days_back)
            except Exception as exc:
                logger.error("Apify trending content failed: %s", exc)
        # Fallback reuse fetch_reels with heuristic count
        return self.fetch_reels(competitors, count=len(competitors) * 5 or 10)

