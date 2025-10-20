"""Submagic API client STUB - заглушка для экономии кредитов."""
from __future__ import annotations

import time
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SubmagicClient:
    """Submagic API client STUB - заглушка для экономии кредитов."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._video_urls = {}  # Кеш для хранения исходных URL видео
        logger.info("Submagic API: Используется заглушка (API отключен для экономии кредитов)")

    def create_project(self, video_url: str, language: str, template_name: str = None) -> Dict[str, Any]:
        """Create a new Submagic project with video processing settings."""
        # ЗАГЛУШКА: Submagic API временно отключен
        logger.info("Submagic API: Используется заглушка (API отключен для экономии кредитов)")
        
        project_id = f"submagic_{int(time.time())}"
        # Сохраняем исходный URL для последующего использования
        self._video_urls[project_id] = video_url
        
        return {
            "id": project_id,
            "status": "completed",
            "message": "Submagic API отключен (заглушка) - возвращаем исходное видео",
            "videoUrl": video_url  # Возвращаем исходное HeyGen видео
        }

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project status and details."""
        # ЗАГЛУШКА: Submagic API временно отключен
        logger.info(f"Submagic API: Заглушка для проекта {project_id}")
        
        if project_id in self._video_urls:
            return {
                "id": project_id,
                "status": "completed",
                "videoUrl": self._video_urls[project_id],
                "message": "Submagic API отключен (заглушка)"
            }
        else:
            return {
                "id": project_id,
                "status": "error",
                "message": "Проект не найден (заглушка)"
            }

    def wait_for_completion(self, project_id: str, progress_callback=None) -> Dict[str, Any]:
        """Wait for project completion."""
        # ЗАГЛУШКА: Сразу возвращаем завершенный проект
        logger.info(f"Submagic API: Заглушка - проект {project_id} сразу завершен")
        
        if progress_callback:
            progress_callback(100)  # Сразу 100% прогресс
        
        return self.get_project(project_id)

    def export_project(self, project_id: str) -> Dict[str, Any]:
        """Export project."""
        # ЗАГЛУШКА: Возвращаем исходное видео
        logger.info(f"Submagic API: Заглушка - экспорт проекта {project_id}")
        
        if project_id in self._video_urls:
            return {
                "videoUrl": self._video_urls[project_id],
                "message": "Submagic API отключен (заглушка) - исходное видео"
            }
        else:
            return {
                "videoUrl": None,
                "message": "Проект не найден (заглушка)"
            }

    def download_video(self, video_url: str, output_path: str) -> str:
        """Download video."""
        # ЗАГЛУШКА: Копируем исходное видео
        logger.info(f"Submagic API: Заглушка - копируем исходное видео")
        
        import shutil
        import os
        
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Копируем исходное видео (заглушка)
        shutil.copy2(video_url.replace('http://72.56.66.228', '/root'), output_path)
        
        return output_path

    def get_templates(self) -> List[Dict[str, Any]]:
        """Get available templates."""
        # ЗАГЛУШКА: Возвращаем базовые шаблоны
        return [
            {"id": "hormozi2", "name": "Hormozi 2"},
            {"id": "modern", "name": "Modern"},
            {"id": "classic", "name": "Classic"},
            {"id": "minimal", "name": "Minimal"}
        ]

    def get_languages(self) -> List[Dict[str, Any]]:
        """Get available languages."""
        # ЗАГЛУШКА: Возвращаем базовые языки
        return [
            {"code": "ru", "name": "Русский"},
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Español"},
            {"code": "fr", "name": "Français"},
            {"code": "de", "name": "Deutsch"},
            {"code": "it", "name": "Italiano"}
        ]
