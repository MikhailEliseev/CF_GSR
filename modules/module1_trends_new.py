from celery_app import celery_app
from modules.base_module import BaseModule
from models import db, Competitors
from services import ApifyService, AssemblyService, OpenAIService, ElevenLabsService, HeyGenService
from typing import List, Dict, Any


class TrendModule(BaseModule):
    """
    Модуль трендвотчинга и анализа конкурентов с новой архитектурой
    """

    def __init__(self):
        super().__init__('trends')

        api_keys = self.settings.get_api_keys()
        
        # Инициализация сервисов
        self.apify_service = ApifyService(api_keys.get('apify_api_key'))
        self.assembly_service = AssemblyService(api_keys.get('assemblyai_api_key'))
        self.openai_service = OpenAIService(api_keys.get('openai_api_key'))
        self.elevenlabs_service = ElevenLabsService(api_keys.get('elevenlabs_api_key'))
        self.heygen_service = HeyGenService(api_keys.get('heygen_api_key'))

    def prepare_context(self, viral_posts: List[Dict] = None) -> str:
        """
        Подготовка контекста на основе вирального контента
        """
        if not viral_posts:
            return "Анализ трендов в социальных сетях"

        top_posts = viral_posts[:5]
        context_parts = []
        for i, post in enumerate(top_posts, 1):
            context_parts.append(f"""
            Пост {i}:
            - Автор: {post.get('source_username', 'Неизвестно')}
            - Просмотры: {post.get('views_count', 0):,}
            - Лайки: {post.get('likes_count', 0):,}
            - Описание: {post.get('caption', '')[:200]}...
            """)

        context = f"""
        Анализ топ {len(top_posts)} вирального контента:

        {''.join(context_parts)}

        На основе этого анализа создайте текст для видео, который:
        1. Объясняет текущие тренды
        2. Даёт советы по созданию вирального контента
        3. Мотивирует зрителей
        """

        return context

    def analyze_competitors(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Анализ конкурентов с использованием ApifyService
        """
        competitors = Competitors.query.filter_by(is_active=True).all()
        competitor_usernames = [c.username for c in competitors]
        
        if not competitor_usernames:
            return []

        # Используем новый сервисный слой
        reels = self.apify_service.fetch_reels(competitor_usernames, count=20)
        
        # Фильтруем виральные посты
        viral_posts = [post for post in reels if post.get('is_viral') or (post.get('views_count') or 0) > 30000]
        
        return viral_posts

    def transcribe_video(self, video_url: str) -> str:
        """
        Транскрибация видео с использованием AssemblyService
        """
        return self.assembly_service.transcribe(video_url)

    def rewrite_text(self, transcript: str) -> str:
        """
        Переписывание текста с использованием OpenAIService
        """
        return self.openai_service.rewrite_transcript(transcript, self.settings.master_prompt)

    def generate_audio(self, text: str, voice_id: str = None) -> str:
        """
        Генерация аудио с использованием ElevenLabsService
        """
        if not voice_id:
            additional = self.settings.get_additional_settings()
            voice_id = additional.get('default_voice_id', 'demo_voice')
        
        return self.elevenlabs_service.generate_audio(text, voice_id)

    def generate_video(self, audio_url: str, avatar_id: str = None) -> Dict:
        """
        Создание видео с использованием HeyGenService
        """
        if not avatar_id:
            additional = self.settings.get_additional_settings()
            avatar_id = additional.get('default_avatar_id', 'demo_avatar')
        
        return self.heygen_service.generate_video(audio_url, avatar_id)

    def get_available_voices(self) -> List[Dict]:
        """
        Получение списка доступных голосов
        """
        return self.elevenlabs_service.list_voices()

    def get_available_avatars(self) -> List[Dict]:
        """
        Получение списка доступных аватаров
        """
        return self.heygen_service.list_avatars()
