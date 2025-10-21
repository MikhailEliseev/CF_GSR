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

    def test_integrations(self) -> Dict[str, bool]:
        """Тестирование интеграций"""
        results = {}

        results['apify'] = self.apify_service.test_connection() if self.apify_service else False
        results['openai'] = self.openai_service.test_connection(self.settings.openai_assistant_id) if self.openai_service else False
        results['elevenlabs'] = self.elevenlabs_service.test_connection() if self.elevenlabs_service else False
        results['heygen'] = self.heygen_service.test_connection() if self.heygen_service else False
        results['storage'] = self.storage_client.test_connection()

        return results

    @celery_app.task(bind=True)
    def start_generation(self, task_id: str, days_back: int = 7,
                         voice_id: str = None, avatar_id: str = None):
        """
        Запуск полного пайплайна генерации с пошаговым прогрессом
        """
        try:
            module = TrendModule()

            additional_settings = module.settings.get_additional_settings()
            if not voice_id:
                voice_id = additional_settings.get('default_voice_id')
            if not avatar_id:
                avatar_id = additional_settings.get('default_avatar_id')

            if not voice_id or not avatar_id:
                raise Exception("Voice ID and Avatar ID must be specified")

            # Шаг 1: Анализ конкурентов
            module.update_task_progress(task_id, 10, "Анализ конкурентов...")
            viral_posts = module.analyze_competitors(days_back)

            if not viral_posts:
                raise Exception("No viral content found")

            # Шаг 2: Подготовка контекста
            module.update_task_progress(task_id, 20, "Подготовка контекста...")
            context = module.prepare_context(viral_posts)

            # Шаг 3: Генерация текста
            module.update_task_progress(task_id, 30, "Генерация текста...")
            text = module.generate_text_content(context)
            if not text:
                raise Exception("Failed to generate text")

            # Шаг 4: Генерация речи
            module.update_task_progress(task_id, 50, "Генерация речи...")
            audio_url = module.generate_audio(text, voice_id)
            if not audio_url:
                raise Exception("Failed to generate speech")

            # Шаг 5: Генерация видео
            module.update_task_progress(task_id, 70, "Генерация видео...")
            video_info = module.generate_video(audio_url, avatar_id)
            if not video_info:
                raise Exception("Failed to generate video")

            # Шаг 6: Сохранение результата
            module.update_task_progress(task_id, 90, "Сохранение результата...")
            video_url = video_info.get('video_url') if isinstance(video_info, dict) else video_info
            module.save_generation_result(task_id, text, audio_url, video_url, avatar_id, voice_id)

            # Завершение
            result_data = {
                'text': text,
                'audio_url': audio_url,
                'video_url': video_url,
                'avatar_id': avatar_id,
                'voice_id': voice_id,
                'viral_posts_analyzed': len(viral_posts),
                'top_viral_post': viral_posts[0] if viral_posts else None
            }
            module.update_task_progress(task_id, 100, "Готово!", result_data=result_data)

            return result_data

        except Exception as e:
            module = TrendModule()
            module.update_task_progress(task_id, 0, "Ошибка", error_message=str(e))
            raise e

    def start_step_by_step_generation(self, task_id: str, step: str, **kwargs):
        """
        Запуск пошаговой генерации
        """
        try:
            module = TrendModule()
            
            if step == "analyze":
                # Анализ конкурентов
                module.update_task_progress(task_id, 10, "Анализ конкурентов...")
                days_back = kwargs.get('days_back', 7)
                viral_posts = module.analyze_competitors(days_back)
                
                result_data = {
                    'viral_posts': viral_posts,
                    'viral_posts_count': len(viral_posts)
                }
                module.update_task_progress(task_id, 20, "Анализ завершен", result_data=result_data)
                return result_data
                
            elif step == "transcribe":
                # Транскрибация
                module.update_task_progress(task_id, 30, "Транскрибация видео...")
                video_url = kwargs.get('video_url')
                if not video_url:
                    raise Exception("Video URL required for transcription")
                
                transcript = module.transcribe_video(video_url)
                result_data = {'transcript': transcript}
                module.update_task_progress(task_id, 40, "Транскрибация завершена", result_data=result_data)
                return result_data
                
            elif step == "rewrite":
                # Переписывание
                module.update_task_progress(task_id, 50, "Переписывание текста...")
                transcript = kwargs.get('transcript')
                if not transcript:
                    raise Exception("Transcript required for rewriting")
                
                rewritten = module.rewrite_text(transcript)
                result_data = {'rewritten_text': rewritten}
                module.update_task_progress(task_id, 60, "Переписывание завершено", result_data=result_data)
                return result_data
                
            elif step == "voice":
                # Генерация озвучки
                module.update_task_progress(task_id, 70, "Генерация озвучки...")
                text = kwargs.get('text')
                voice_id = kwargs.get('voice_id')
                if not text:
                    raise Exception("Text required for voice generation")
                
                audio_url = module.generate_audio(text, voice_id)
                result_data = {'audio_url': audio_url}
                module.update_task_progress(task_id, 80, "Озвучка завершена", result_data=result_data)
                return result_data
                
            elif step == "video":
                # Создание видео
                module.update_task_progress(task_id, 90, "Создание видео...")
                audio_url = kwargs.get('audio_url')
                avatar_id = kwargs.get('avatar_id')
                if not audio_url:
                    raise Exception("Audio URL required for video generation")
                
                video_info = module.generate_video(audio_url, avatar_id)
                video_url = video_info.get('video_url') if isinstance(video_info, dict) else video_info
                result_data = {'video_url': video_url, 'video_info': video_info}
                module.update_task_progress(task_id, 100, "Видео создано", result_data=result_data)
                return result_data
                
            else:
                raise Exception(f"Unknown step: {step}")
                
        except Exception as e:
            module = TrendModule()
            module.update_task_progress(task_id, 0, "Ошибка", error_message=str(e))
            raise e
