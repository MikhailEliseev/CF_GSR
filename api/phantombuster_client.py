"""PhantomBuster API client for Instagram scraping with real statistics."""
from __future__ import annotations

import requests
import time
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PhantomBusterClient:
    """PhantomBuster API client for Instagram data collection with real statistics."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.phantombuster.com/api/v2"
        self.headers = {
            "X-Phantombuster-Key": api_key,
            "Content-Type": "application/json"
        }

    def start_agent(self, agent_id: str, arguments: Dict[str, Any]) -> str:
        """Start a PhantomBuster agent and return container ID."""
        try:
            url = f"{self.base_url}/agents/{agent_id}/launch"
            data = {"argument": arguments}
            
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            container_id = result.get("containerId")
            
            if not container_id:
                raise Exception(f"No container ID returned: {result}")
            
            logger.info(f"Started PhantomBuster agent {agent_id}, container: {container_id}")
            return container_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to start PhantomBuster agent: {e}")
            raise Exception(f"Failed to start agent: {str(e)}")

    def get_agent_result(self, container_id: str) -> Dict[str, Any]:
        """Get the result of a PhantomBuster agent execution."""
        try:
            url = f"{self.base_url}/containers/fetch-output"
            params = {"id": container_id}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get agent result: {e}")
            raise Exception(f"Failed to get result: {str(e)}")

    def wait_for_completion(self, container_id: str, max_wait_time: int = 600) -> Dict[str, Any]:
        """Wait for agent completion with polling."""
        start_time = time.time()
        max_attempts = max_wait_time // 10  # Poll every 10 seconds
        
        for attempt in range(max_attempts):
            try:
                result = self.get_agent_result(container_id)
                status = result.get("status", "unknown")
                
                if status == "finished":
                    logger.info(f"Agent completed successfully in {time.time() - start_time:.1f}s")
                    return result
                elif status == "error":
                    error_msg = result.get("error", "Unknown error")
                    logger.error(f"Agent failed: {error_msg}")
                    raise Exception(f"Agent execution failed: {error_msg}")
                
                # Still running, wait and retry
                elapsed = time.time() - start_time
                logger.info(f"Agent still running... ({elapsed:.1f}s elapsed)")
                time.sleep(10)
                
            except Exception as e:
                if "Agent execution failed" in str(e):
                    raise
                logger.warning(f"Polling attempt {attempt + 1} failed: {e}")
                time.sleep(10)
        
        raise Exception(f"Agent did not complete within {max_wait_time} seconds")

    def fetch_instagram_posts(self, usernames: List[str], count: int = 10, agent_id: str = None) -> List[Dict[str, Any]]:
        """Fetch Instagram posts with real statistics using PhantomBuster."""
        if not agent_id:
            # Default Instagram Profile Scraper agent ID - needs to be configured
            agent_id = "YOUR_INSTAGRAM_AGENT_ID"
        
        try:
            # Prepare arguments for the agent
            arguments = {
                "sessionCookie": "YOUR_SESSION_COOKIE",  # Needs to be configured
                "spreadsheetUrl": "",  # Optional: Google Sheets URL
                "numberOfProfiles": len(usernames),
                "profiles": usernames,
                "numberOfPostsPerProfile": count,
                "includeStories": False,
                "includeHighlights": False
            }
            
            logger.info(f"Starting Instagram data collection for {len(usernames)} profiles")
            
            # Start the agent
            container_id = self.start_agent(agent_id, arguments)
            
            # Wait for completion
            result = self.wait_for_completion(container_id)
            
            # Extract data from result
            data = result.get("data", [])
            
            if not data:
                logger.warning("No data returned from PhantomBuster")
                return []
            
            # Normalize data format to match Apify format
            normalized_posts = []
            for post in data:
                normalized_post = {
                    "id": post.get("id", ""),
                    "source_username": post.get("username", ""),
                    "video_url": post.get("videoUrl", ""),
                    "thumbnail_url": post.get("thumbnailUrl", ""),
                    "caption": post.get("caption", ""),
                    "likes_count": post.get("likes", 0),
                    "comments_count": post.get("comments", 0),
                    "views_count": post.get("views", 0),
                    "timestamp": post.get("timestamp", ""),
                    "is_viral": self._is_viral_post(post),
                    "source": "phantombuster"
                }
                normalized_posts.append(normalized_post)
            
            logger.info(f"Successfully collected {len(normalized_posts)} posts with real statistics")
            return normalized_posts
            
        except Exception as e:
            logger.error(f"Failed to fetch Instagram posts: {e}")
            raise Exception(f"Instagram data collection failed: {str(e)}")

    def _is_viral_post(self, post: Dict[str, Any]) -> bool:
        """Determine if a post is viral based on engagement metrics."""
        likes = post.get("likes", 0)
        comments = post.get("comments", 0)
        views = post.get("views", 0)
        
        # Viral criteria: high engagement or views
        return (
            likes > 1000 or 
            comments > 100 or 
            views > 10000 or
            (likes > 500 and comments > 50)
        )

    def test_connection(self) -> bool:
        """Test if the API key is valid."""
        try:
            url = f"{self.base_url}/agents"
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except:
            return False
