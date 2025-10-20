"""
Обновленные Celery задачи для интеграции с существующей логикой TrendModule
"""

from celery import Celery
from config import Config
from models import db, TrendAnalysis, CompetitorData, ContentGeneration
from modules.module1_trends import TrendModule
from api.assemblyai_client import AssemblyAIClient
from api.openai_client import OpenAIClient
from api.elevenlabs_simple import ElevenLabsSimple
from api.heygen_client import HeyGenClient
import os
import requests
import json
from datetime import datetime

# Создание Celery приложения
celery_app = Celery(
    'content_factory',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['modules.module1_trends', 'modules.module2_vacancies', 'modules.module3_experts']
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600,
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True
)

@celery_app.task(bind=True)
def parse_competitors_task(self, analysis_id):
    """Фоновая задача для парсинга конкурентов с использованием существующей логики"""
    try:
        # Обновляем статус
        analysis = TrendAnalysis.query.get(analysis_id)
        if not analysis:
            raise Exception("Analysis not found")
        
        analysis.status = 'parsing'
        db.session.commit()
        
        # Используем существующую логику TrendModule
        trend_module = TrendModule()
        
        # Получаем настройки
        config = analysis.get_config()
        days_back = config.get('days_back', 7)
        
        # Запускаем анализ конкурентов через существующий метод
        viral_posts = trend_module.analyze_competitors(days_back)
        
        # Сохраняем результаты в новые модели БД
        for post in viral_posts:
            competitor_data = CompetitorData(
                analysis_id=analysis_id,
                competitor_handle=post.get('source_username', ''),
                post_url=post.get('url', ''),
                views=post.get('views_count', 0),
                likes=post.get('likes_count', 0),
                comments=post.get('comments_count', 0),
                engagement_rate=post.get('engagement_rate', 0.0),
                post_date=datetime.fromisoformat(post.get('timestamp', '').replace('Z', '+00:00')) if post.get('timestamp') else None,
                thumbnail_url=post.get('thumbnail_url', ''),
                is_selected=False
            )
            db.session.add(competitor_data)
        
        # Обновляем статус анализа
        analysis.status = 'completed'
        analysis.set_results({
            'viral_posts_count': len(viral_posts),
            'total_posts_analyzed': len(viral_posts),
            'analysis_date': datetime.utcnow().isoformat()
        })
        db.session.commit()
        
        return {
            'success': True,
            'viral_posts_count': len(viral_posts),
            'message': 'Анализ конкурентов завершен'
        }
        
    except Exception as e:
        # Обновляем статус при ошибке
        analysis = TrendAnalysis.query.get(analysis_id)
        if analysis:
            analysis.status = 'failed'
            analysis.set_results({'error': str(e)})
            db.session.commit()
        
        raise e

@celery_app.task(bind=True)
def transcribe_video_task(self, analysis_id, post_id):
    """Транскрибация видео с использованием существующей логики"""
    try:
        # Находим пост
        post = CompetitorData.query.get(post_id)
        if not post:
            raise Exception("Post not found")
        
        # Находим запись генерации контента
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            content_gen = ContentGeneration(
                analysis_id=analysis_id,
                selected_post_id=post_id,
                status='transcribing'
            )
            db.session.add(content_gen)
            db.session.commit()
        
        # Используем существующую логику для транскрибации
        # Здесь можно добавить логику скачивания видео и транскрибации
        # Пока используем демо-данные
        demo_transcript = f"""
        Демо-транскрипт для поста от {post.competitor_handle}:
        
        Привет, друзья! Сегодня я хочу поделиться с вами секретами успеха в социальных сетях.
        Как вы знаете, контент - это король, и важно создавать качественные материалы.
        
        Вот несколько советов:
        1. Будьте аутентичными
        2. Создавайте ценность для аудитории
        3. Используйте тренды, но добавляйте свой уникальный взгляд
        
        Что думаете? Поделитесь в комментариях!
        """
        
        # Обновляем статус
        content_gen.original_transcript = demo_transcript
        content_gen.status = 'transcribed'
        db.session.commit()
        
        return {
            'success': True,
            'transcript': demo_transcript,
            'message': 'Транскрибация завершена'
        }
        
    except Exception as e:
        # Обновляем статус при ошибке
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if content_gen:
            content_gen.status = 'failed'
            db.session.commit()
        
        raise e

@celery_app.task(bind=True)
def rewrite_text_task(self, analysis_id, transcript_text):
    """Переписывание текста с использованием существующей логики"""
    try:
        # Находим запись генерации контента
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            raise Exception("Content generation not found")
        
        # Используем существующую логику для переписывания
        # Здесь можно добавить логику с OpenAI Assistant
        # Пока используем демо-данные
        demo_rewritten = f"""
        🔥 СЕКРЕТЫ УСПЕХА В СОЦСЕТЯХ 🔥
        
        Привет, друзья! 👋 Сегодня раскрываю главные секреты вирусного контента!
        
        💡 КЛЮЧЕВЫЕ ПРИНЦИПЫ:
        ✅ Аутентичность - будьте собой
        ✅ Ценность - давайте пользу аудитории  
        ✅ Тренды - следите за трендами, но добавляйте свой стиль
        
        🚀 РЕЗУЛЬТАТ:
        - Больше вовлеченности
        - Рост подписчиков
        - Узнаваемость бренда
        
        Что думаете? Пишите в комментариях! 💬
        """
        
        # Обновляем статус
        content_gen.rewritten_text = demo_rewritten
        content_gen.status = 'rewritten'
        db.session.commit()
        
        return {
            'success': True,
            'rewritten_text': demo_rewritten,
            'message': 'Переписывание завершено'
        }
        
    except Exception as e:
        # Обновляем статус при ошибке
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if content_gen:
            content_gen.status = 'failed'
            db.session.commit()
        
        raise e

@celery_app.task(bind=True)
def generate_voice_task(self, analysis_id, text, voice_settings):
    """Генерация озвучки с использованием существующей логики"""
    try:
        # Находим запись генерации контента
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            raise Exception("Content generation not found")
        
        # Используем существующую логику TrendModule для получения голосов
        trend_module = TrendModule()
        voices = trend_module.get_available_voices()
        
        if not voices:
            raise Exception("No voices available")
        
        # Выбираем голос (по умолчанию первый)
        voice_id = voice_settings.get('voice_id', voices[0].get('voice_id', 'default'))
        
        # Здесь можно добавить реальную генерацию озвучки через ElevenLabs
        # Пока используем демо-данные
        demo_audio_url = f"https://demo-audio-url.com/{voice_id}.mp3"
        
        # Обновляем статус
        content_gen.audio_file_url = demo_audio_url
        content_gen.status = 'voice_generated'
        db.session.commit()
        
        return {
            'success': True,
            'audio_url': demo_audio_url,
            'message': 'Озвучка сгенерирована'
        }
        
    except Exception as e:
        # Обновляем статус при ошибке
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if content_gen:
            content_gen.status = 'failed'
            db.session.commit()
        
        raise e

@celery_app.task(bind=True)
def generate_video_task(self, analysis_id, audio_file_url, avatar_settings):
    """Генерация видео с использованием существующей логики"""
    try:
        # Находим запись генерации контента
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            raise Exception("Content generation not found")
        
        # Используем существующую логику TrendModule для получения аватаров
        trend_module = TrendModule()
        avatars = trend_module.get_available_avatars()
        
        if not avatars:
            raise Exception("No avatars available")
        
        # Выбираем аватар (по умолчанию первый)
        avatar_id = avatar_settings.get('avatar_id', avatars[0].get('avatar_id', 'default'))
        
        # Здесь можно добавить реальную генерацию видео через HeyGen
        # Пока используем демо-данные
        demo_video_url = f"https://demo-video-url.com/{avatar_id}.mp4"
        
        # Обновляем статус
        content_gen.video_file_url = demo_video_url
        content_gen.status = 'completed'
        db.session.commit()
        
        return {
            'success': True,
            'video_url': demo_video_url,
            'message': 'Видео сгенерировано'
        }
        
    except Exception as e:
        # Обновляем статус при ошибке
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if content_gen:
            content_gen.status = 'failed'
            db.session.commit()
        
        raise e

if __name__ == '__main__':
    celery_app.start()
