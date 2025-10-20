from celery_app import celery_app
from modules.base_module import BaseModule
from models import db, Competitors
from services import ApifyService, ElevenLabsService
from typing import List, Dict, Any


class TrendModule(BaseModule):
    """
    Модуль трендвотчинга и анализа конкурентов
    """

    def __init__(self):
        super().__init__('trends')
        # BaseModule уже инициализирует все сервисы, включая elevenlabs_service

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

    def get_competitors(self) -> List[str]:
        competitors = Competitors.query.filter_by(is_active=True).all()
        return [comp.username for comp in competitors]

    def analyze_competitors(self, days_back: int = 7) -> List[Dict[str, Any]]:
        if not self.apify_service:
            raise Exception("Apify client not configured")

        competitors = self.get_competitors()
        if not competitors:
            raise Exception("No active competitors found")

        viral_posts = self.apify_service.get_trending_content(competitors, days_back)

        for competitor in competitors:
            comp_obj = Competitors.query.filter_by(username=competitor).first()
            if comp_obj:
                comp_obj.last_checked = db.func.now()

        db.session.commit()
        return viral_posts

    @celery_app.task(bind=True)
    def start_generation(self, task_id: str, days_back: int = 7,
                         voice_id: str = None, avatar_id: str = None):
        try:
            module = TrendModule()

            additional_settings = module.settings.get_additional_settings()
            if not voice_id:
                voice_id = additional_settings.get('default_voice_id')
            if not avatar_id:
                avatar_id = additional_settings.get('default_avatar_id')

            if not voice_id or not avatar_id:
                raise Exception("Voice ID and Avatar ID must be specified")

            module.update_task_progress(task_id, 5, "Анализ конкурентов...")
            viral_posts = module.analyze_competitors(days_back)

            if not viral_posts:
                raise Exception("No viral content found")

            module.update_task_progress(task_id, 10, "Подготовка контекста...")
            context = module.prepare_context(viral_posts)

            result = module.execute_full_pipeline(task_id, context, voice_id, avatar_id)

            result['viral_posts_analyzed'] = len(viral_posts)
            result['top_viral_post'] = viral_posts[0] if viral_posts else None

            module.update_task_progress(task_id, 100, "Готово!", result_data=result)

            return result

        except Exception as e:
            module = TrendModule()
            module.update_task_progress(task_id, 0, "Ошибка", error_message=str(e))
            raise e

    def get_available_voices(self) -> List[Dict]:
        if not self.elevenlabs_service:
            return []
        return self.elevenlabs_service.list_voices()

    def get_available_avatars(self) -> List[Dict]:
        if not self.heygen_service:
            return []
        return self.heygen_service.list_avatars()

    def test_integrations(self) -> Dict[str, bool]:
        results = {}

        results['apify'] = self.apify_service.test_connection() if self.apify_service else False
        results['openai'] = self.openai_service.test_connection(self.settings.openai_assistant_id) if self.openai_service else False
        results['elevenlabs'] = self.elevenlabs_service.test_connection() if self.elevenlabs_service else False
        results['heygen'] = self.heygen_service.test_connection() if self.heygen_service else False
        results['storage'] = self.storage_client.test_connection()

        return results
