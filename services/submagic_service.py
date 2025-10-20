"""Service abstraction around Submagic video processing with captions and effects."""
from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class SubmagicService:
    """Encapsulates Submagic video processing with safe fallbacks."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ""
        self._client = None
        if self.api_key:
            try:
                from api.submagic_client_stub import SubmagicClient  # lazy import - используем заглушку
                self._client = SubmagicClient(self.api_key)
                logger.info("Submagic API: Используется заглушка для экономии кредитов")
            except Exception as exc:
                logger.warning("Failed to initialise Submagic client: %s", exc)
                self._client = None

    def add_captions(self, video_url: str, settings: Dict, progress_callback=None) -> str:
        """
        Add captions and effects to video using Submagic.
        
        Args:
            video_url: URL of the video to process
            settings: Dictionary with processing settings:
                - language: str (e.g., 'ru', 'en')
                - template_name: str (e.g., 'Hormozi 2')
                - magic_brolls: bool
                - brolls_percentage: int (0-100)
                - magic_zooms: bool
                - background_music: bool
        
        Returns:
            Path to the processed video file
        """
        if not self._client:
            logger.warning("Submagic client not available, cannot process video")
            raise Exception("Submagic API key not configured")

        try:
            # Extract settings with defaults
            language = settings.get('language', 'ru')
            template_name = settings.get('template_name', 'Hormozi 2')
            magic_brolls = settings.get('magic_brolls', False)
            brolls_percentage = settings.get('brolls_percentage', 0)
            magic_zooms = settings.get('magic_zooms', False)
            background_music = settings.get('background_music', False)
            
            logger.info(f"Starting Submagic processing for video: {video_url}")
            logger.info(f"Settings: language={language}, template={template_name}, "
                       f"brolls={magic_brolls}({brolls_percentage}%), zooms={magic_zooms}, music={background_music}")
            
            # Create project
            project = self._client.create_project(
                video_url=video_url,
                language=language,
                template_name=template_name
            )
            
            project_id = project.get('id')
            if not project_id:
                raise Exception("No project ID returned from Submagic")
            
            logger.info(f"Created Submagic project: {project_id}")
            
            # Wait for completion with progress callback
            completed_project = self._client.wait_for_completion(project_id, progress_callback=progress_callback)
            
            # Export the project
            export_result = self._client.export_project(project_id)
            export_url = export_result.get('videoUrl')
            
            if not export_url:
                raise Exception("No video URL in export result")
            
            # Check if we got the original video URL (fallback case)
            if export_url == video_url:
                # Submagic API недоступен - возвращаем исходное видео без обработки
                logger.info("Submagic API недоступен - возвращаем исходное видео без обработки")
                return video_url
            else:
                # Download the processed video
                output_filename = f"caption_{uuid.uuid4().hex[:8]}.mp4"
                output_path = os.path.join("static", "video", output_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                self._client.download_video(export_url, output_path)
                
                logger.info(f"Successfully processed video: {output_path}")
                return output_path
            
        except Exception as exc:
            logger.error(f"Submagic processing failed: {exc}")
            raise Exception(f"Video processing failed: {str(exc)}")

    def get_templates(self) -> List[Dict[str, Any]]:
        """Get available templates."""
        if not self._client:
            return []
        
        try:
            return self._client.get_templates()
        except Exception:
            return []

    def get_languages(self) -> List[Dict[str, Any]]:
        """Get supported languages."""
        if not self._client:
            return []
        
        try:
            return self._client.get_languages()
        except Exception:
            return []

    def test_connection(self) -> bool:
        """Test if Submagic API is accessible."""
        if not self._client:
            return False
        
        try:
            return self._client.test_connection()
        except Exception:
            return False
