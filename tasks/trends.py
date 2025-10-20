"""Celery tasks backing the trends module."""
from __future__ import annotations

from celery_app import celery_app
from app import create_app
from models import db, TrendAnalysis, CompetitorData, ContentGeneration, Settings
from modules.module1_trends import TrendModule
from services import AssemblyService
from datetime import datetime
from typing import Dict, Any

flask_app, _ = create_app()


def _get_trends_settings() -> Settings | None:
    with flask_app.app_context():
        return Settings.query.filter_by(module_name='trends').first()


@celery_app.task(bind=True)
def parse_competitors_task(self, analysis_id):
    with flask_app.app_context():
        analysis = TrendAnalysis.query.get(analysis_id)
        if not analysis:
            raise Exception("Analysis not found")

        analysis.status = 'parsing'
        db.session.commit()

        trend_module = TrendModule()

        config = analysis.get_config()
        days_back = config.get('days_back', 7)

        viral_posts = trend_module.analyze_competitors(days_back)

        for post in viral_posts:
            competitor_data = CompetitorData(
                analysis_id=analysis_id,
                competitor_handle=post.get('source_username', ''),
                post_url=post.get('url') or post.get('video_url', ''),
                views=post.get('views_count', 0),
                likes=post.get('likes_count', 0),
                comments=post.get('comments_count', 0),
                engagement_rate=post.get('engagement_rate', 0.0),
                post_date=datetime.fromisoformat(post.get('timestamp')) if post.get('timestamp') else None,
                thumbnail_url=post.get('thumbnail_url', ''),
                is_selected=False
            )
            db.session.add(competitor_data)

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


@celery_app.task(bind=True)
def transcribe_video_task(self, analysis_id, post_id):
    with flask_app.app_context():
        post = CompetitorData.query.get(post_id)
        if not post:
            raise Exception("Post not found")

        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            content_gen = ContentGeneration(
                analysis_id=analysis_id,
                selected_post_id=post_id,
                status='transcribing'
            )
            db.session.add(content_gen)
            db.session.commit()

        settings = _get_trends_settings()
        api_keys = settings.get_api_keys() if settings else {}
        assembly_service = AssemblyService(api_keys.get('assemblyai_api_key'))

        transcript = assembly_service.transcribe(post.post_url or post.thumbnail_url or '')

        content_gen.original_transcript = transcript
        content_gen.status = 'transcribed'
        db.session.commit()

        return {
            'success': True,
            'transcript': transcript,
            'message': 'Транскрибация завершена'
        }


@celery_app.task(bind=True)
def rewrite_text_task(self, analysis_id, transcript_text):
    with flask_app.app_context():
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            raise Exception("Content generation not found")

        trend_module = TrendModule()
        rewritten = trend_module.openai_service.rewrite_transcript(
            transcript_text,
            master_prompt=trend_module.settings.master_prompt
        )

        content_gen.rewritten_text = rewritten
        content_gen.status = 'rewritten'
        db.session.commit()

        return {
            'success': True,
            'rewritten_text': rewritten,
            'message': 'Переписывание завершено'
        }


@celery_app.task(bind=True)
def generate_voice_task(self, analysis_id, text, voice_settings: Dict[str, Any] | None = None):
    with flask_app.app_context():
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            raise Exception("Content generation not found")

        trend_module = TrendModule()
        voice_settings = voice_settings or {}
        voice_id = voice_settings.get('voice_id')
        model_id = voice_settings.get('model_id')

        additional = trend_module.settings.get_additional_settings()
        voice_id = voice_id or additional.get('default_voice_id') or 'demo_voice'
        model_id = model_id or additional.get('default_voice_model')

        audio_url = trend_module.elevenlabs_service.generate_audio(text, voice_id=voice_id, model_id=model_id)

        content_gen.final_text = text
        content_gen.audio_file_url = audio_url
        content_gen.set_generation_settings({**voice_settings, 'resolved_voice_id': voice_id})
        content_gen.status = 'voice_generated'
        db.session.commit()

        return {
            'success': True,
            'audio_url': audio_url,
            'message': 'Озвучка сгенерирована'
        }


@celery_app.task(bind=True)
def generate_video_task(self, analysis_id, audio_file_url, avatar_settings: Dict[str, Any] | None = None):
    with flask_app.app_context():
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            raise Exception("Content generation not found")

        trend_module = TrendModule()
        avatar_settings = avatar_settings or {}
        avatar_id = avatar_settings.get('avatar_id')

        additional = trend_module.settings.get_additional_settings()
        avatar_id = avatar_id or additional.get('default_avatar_id') or 'demo_avatar'

        video_info = trend_module.heygen_service.generate_video(audio_file_url, avatar_id)
        video_url = video_info.get('video_url') if isinstance(video_info, dict) else video_info

        content_gen.video_file_url = video_url
        content_gen.status = 'completed'
        db.session.commit()

        response = {'success': True, 'message': 'Видео сгенерировано'}
        response.update(video_info if isinstance(video_info, dict) else {'video_url': video_url})
        return response
