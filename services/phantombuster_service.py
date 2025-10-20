"""Service abstraction around PhantomBuster Instagram scraping with graceful fallbacks."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)


class PhantomBusterService:
    """Encapsulates PhantomBuster Instagram scraping with safe fallbacks."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ""
        self._client = None
        if self.api_key:
            try:
                from api.phantombuster_client import PhantomBusterClient  # lazy import
                self._client = PhantomBusterClient(self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise PhantomBuster client: %s", exc)
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
        """Build fallback data when PhantomBuster is unavailable."""
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
                        "caption": f"Demo reel {reel_index + 1} from @{competitor} - PhantomBuster fallback data",
                        "likes_count": 100 + (reel_index * 50),
                        "comments_count": 10 + (reel_index * 5),
                        "views_count": 1000 + (reel_index * 200),
                        "timestamp": (now - timedelta(days=reel_index)).isoformat(),
                        "is_viral": reel_index == 0,  # First reel is "viral"
                        "source": "phantombuster_fallback"
                    }
                )
        return fallback

    def fetch_reels(self, competitors: List[str], count: int = 10) -> List[Dict]:
        """
        Fetch Instagram reels using PhantomBuster with real statistics.
        
        Args:
            competitors: List of Instagram usernames (with or without @)
            count: Number of posts to fetch per competitor
            
        Returns:
            List of reel dictionaries with real engagement metrics
        """
        if not self._client:
            logger.warning("PhantomBuster client not available, using fallback data")
            return self._build_fallback(competitors, count)

        try:
            # Normalize competitor handles
            normalised_competitors = self._normalise_handles(competitors)
            if not normalised_competitors:
                logger.warning("No valid competitors provided")
                return []

            logger.info(f"Fetching Instagram data for {len(normalised_competitors)} competitors via PhantomBuster")
            
            # Fetch posts with real statistics
            posts = self._client.fetch_instagram_posts(normalised_competitors, count)
            
            if not posts:
                logger.warning("No posts returned from PhantomBuster, using fallback")
                return self._build_fallback(competitors, count)
            
            logger.info(f"Successfully fetched {len(posts)} posts with real statistics")
            return posts
            
        except Exception as exc:
            logger.error(f"PhantomBuster data collection failed: {exc}")
            logger.info("Falling back to demo data")
            return self._build_fallback(competitors, count)

    def test_connection(self) -> bool:
        """Test if PhantomBuster API is accessible."""
        if not self._client:
            return False
        
        try:
            return self._client.test_connection()
        except Exception:
            return False
