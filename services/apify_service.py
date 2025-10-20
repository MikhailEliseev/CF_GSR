"""Service abstraction around Apify Instagram scraping with graceful fallbacks."""
from __future__ import annotations

import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
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
            except Exception as exc:
                logger.warning("Failed to initialise Apify client: %s", exc)
                self._client = None

    def _normalise_handles(self, competitors: List[str]) -> List[str]:
        """Return cleaned Instagram handles without leading @ or whitespace."""
        normalised: List[str] = []
        for competitor in competitors or []:
            if not competitor:
                continue
            handle = competitor.strip()
            if handle.startswith('@'):
                handle = handle[1:]
            if handle:
                normalised.append(handle)
        return normalised

    def _build_fallback(self, competitors: List[str], count: int) -> List[Dict]:
        fallback: List[Dict] = []
        now = datetime.utcnow()
        for idx, competitor in enumerate(competitors or ["demo_account"]):
            for reel_index in range(min(count, 3)):
                fallback.append(
                    {
                        "id": str(uuid.uuid4()),
                        "source_username": competitor,
                        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBun.mp4",
                        "thumbnail_url": "https://dummyimage.com/400x700/1f7a1f/ffffff.png&text=Demo+Reel",
                        "caption": f"Демо-рилс от {competitor} #{reel_index + 1}",
                        "views_count": 25000 + (reel_index * 15000),
                        "likes_count": 1200 + (reel_index * 800),
                        "comments_count": 45 + (reel_index * 25),
                        "timestamp": (now - timedelta(days=reel_index)).isoformat(),
                        "is_viral": reel_index == 0,
                        "engagement_rate": 0.05 + (reel_index * 0.02),
                    }
                )
        return fallback

    def fetch_reels(self, competitors: List[str], count: int, timeout_seconds: int = 1800) -> List[Dict]:
        """Fetch reels for competitors, falling back to demo data if needed."""
        if count <= 0:
            return []

        safe_count = max(1, min(int(count), 50))
        handles = self._normalise_handles(competitors)

        reels: List[Dict] = []
        errors: List[str] = []

        if self._client and handles:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self._client.get_trending_content,
                    handles,
                    safe_count,
                    7,
                )
                try:
                    reels = future.result(timeout=timeout_seconds) or []
                    if reels:
                        return reels[:safe_count]
                except FuturesTimeout:
                    logger.warning(
                        "Apify request exceeded %s seconds. Falling back to demo data.",
                        timeout_seconds,
                    )
                    errors.append("timeout")
                except Exception as exc:
                    logger.error("Apify request failed: %s", exc)
                    errors.append(str(exc))

        fallback_handles = handles or self._normalise_handles(competitors)
        fallback = self._build_fallback(fallback_handles, safe_count)

        if errors:
            logger.debug("Returning fallback reels due to errors: %s", errors)

        return fallback[:safe_count]
