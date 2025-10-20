"""
Интеграционный слой для модуля трендвотчинга
Связывает существующую логику TrendModule с новыми API endpoints
"""

from flask import Blueprint, request, jsonify
from models import db, TrendAnalysis, CompetitorData, ContentGeneration
from modules.module1_trends import TrendModule
from celery_app import celery_app
import uuid
from datetime import datetime
import json

trends_integration_bp = Blueprint('trends_integration', __name__)

@trends_integration_bp.route('/api/trends/start-analysis', methods=['POST'])
def start_analysis():
    """Запуск анализа трендов с использованием существующей логики"""
    try:
        data = request.get_json()
        
        # Создаем новый анализ в БД
        analysis = TrendAnalysis(
            config=data.get('config', {}),
            status='collecting'
        )
        db.session.add(analysis)
        db.session.commit()
        
        # Используем существующую логику TrendModule
        trend_module = TrendModule()
        
        # Запускаем анализ конкурентов через существующий метод
        days_back = data.get('config', {}).get('days_back', 7)
        viral_posts = trend_module.analyze_competitors(days_back)
        
        # Сохраняем результаты в новые модели БД
        for post in viral_posts:
            competitor_data = CompetitorData(
                analysis_id=analysis.id,
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
        
        return jsonify({
            'success': True,
            'analysis_id': analysis.id,
            'viral_posts_count': len(viral_posts),
            'message': 'Анализ конкурентов завершен'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_integration_bp.route('/api/trends/analysis/<int:analysis_id>/status', methods=['GET'])
def get_analysis_status(analysis_id):
    """Получение статуса анализа"""
    try:
        analysis = TrendAnalysis.query.get_or_404(analysis_id)
        
        return jsonify({
            'success': True,
            'analysis_id': analysis.id,
            'status': analysis.status,
            'config': analysis.get_config(),
            'results': analysis.get_results(),
            'created_at': analysis.created_at.isoformat(),
            'updated_at': analysis.updated_at.isoformat()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_integration_bp.route('/api/trends/analysis/<int:analysis_id>/competitors', methods=['GET'])
def get_competitors(analysis_id):
    """Получение списка конкурентов с использованием существующей логики"""
    try:
        competitors = CompetitorData.query.filter_by(analysis_id=analysis_id).all()
        
        result = []
        for comp in competitors:
            result.append({
                'id': comp.id,
                'competitor_handle': comp.competitor_handle,
                'post_url': comp.post_url,
                'views': comp.views,
                'likes': comp.likes,
                'comments': comp.comments,
                'engagement_rate': comp.engagement_rate,
                'post_date': comp.post_date.isoformat() if comp.post_date else None,
                'thumbnail_url': comp.thumbnail_url,
                'is_selected': comp.is_selected,
                'is_viral': True  # УБРАН ПОРОГ - все посты виральные
            })
        
        return jsonify({
            'success': True,
            'competitors': result
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_integration_bp.route('/api/trends/analysis/<int:analysis_id>/select-post', methods=['POST'])
def select_post(analysis_id):
    """Выбор поста для анализа"""
    try:
        data = request.get_json()
        post_id = data.get('post_id')
        
        # Снимаем выделение с других постов
        CompetitorData.query.filter_by(analysis_id=analysis_id).update({'is_selected': False})
        
        # Выделяем выбранный пост
        post = CompetitorData.query.filter_by(id=post_id, analysis_id=analysis_id).first()
        if post:
            post.is_selected = True
            db.session.commit()
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_integration_bp.route('/api/trends/analysis/<int:analysis_id>/transcribe', methods=['POST'])
def transcribe_video(analysis_id):
    """Транскрибация видео с использованием существующей логики"""
    try:
        # Находим выбранный пост
        selected_post = CompetitorData.query.filter_by(analysis_id=analysis_id, is_selected=True).first()
        if not selected_post:
            return jsonify({'success': False, 'error': 'No post selected'}), 400
        
        # Создаем запись для генерации контента
        content_gen = ContentGeneration(
            analysis_id=analysis_id,
            selected_post_id=selected_post.id,
            status='transcribing'
        )
        db.session.add(content_gen)
        db.session.commit()
        
        # Запускаем транскрибацию через Celery
        from tasks.trends import transcribe_video_task
        task = transcribe_video_task.delay(analysis_id, selected_post.id)
        
        return jsonify({
            'success': True,
            'content_generation_id': content_gen.id,
            'task_id': task.id,
            'message': 'Транскрибация запущена'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_integration_bp.route('/api/trends/analysis/<int:analysis_id>/rewrite', methods=['POST'])
def rewrite_text(analysis_id):
    """Переписывание текста с использованием существующей логики"""
    try:
        data = request.get_json()
        transcript_text = data.get('transcript_text')
        
        if not transcript_text:
            return jsonify({'success': False, 'error': 'No transcript text provided'}), 400
        
        # Находим запись генерации контента
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            return jsonify({'success': False, 'error': 'No content generation found'}), 400
        
        # Обновляем статус
        content_gen.original_transcript = transcript_text
        content_gen.status = 'rewriting'
        db.session.commit()
        
        # Запускаем переписывание через Celery
        from tasks.trends import rewrite_text_task
        task = rewrite_text_task.delay(analysis_id, transcript_text)
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Переписывание запущено'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_integration_bp.route('/api/trends/analysis/<int:analysis_id>/generate-voice', methods=['POST'])
def generate_voice(analysis_id):
    """Генерация озвучки с использованием существующей логики"""
    try:
        data = request.get_json()
        text = data.get('text')
        voice_settings = data.get('voice_settings', {})
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        # Находим запись генерации контента
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            return jsonify({'success': False, 'error': 'No content generation found'}), 400
        
        # Обновляем статус
        content_gen.final_text = text
        content_gen.status = 'generating_voice'
        content_gen.set_generation_settings(voice_settings)
        db.session.commit()
        
        # Запускаем генерацию озвучки через Celery
        from tasks.trends import generate_voice_task
        task = generate_voice_task.delay(analysis_id, text, voice_settings)
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Генерация озвучки запущена'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_integration_bp.route('/api/trends/analysis/<int:analysis_id>/generate-video', methods=['POST'])
def generate_video(analysis_id):
    """Генерация видео с использованием существующей логики"""
    try:
        data = request.get_json()
        audio_file_url = data.get('audio_file_url')
        avatar_settings = data.get('avatar_settings', {})
        
        if not audio_file_url:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        # Находим запись генерации контента
        content_gen = ContentGeneration.query.filter_by(analysis_id=analysis_id).first()
        if not content_gen:
            return jsonify({'success': False, 'error': 'No content generation found'}), 400
        
        # Обновляем статус
        content_gen.audio_file_url = audio_file_url
        content_gen.status = 'generating_video'
        db.session.commit()
        
        # Запускаем генерацию видео через Celery
        from tasks.trends import generate_video_task
        task = generate_video_task.delay(analysis_id, audio_file_url, avatar_settings)
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Генерация видео запущена'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_integration_bp.route('/api/trends/voices', methods=['GET'])
def get_voices():
    """Получение доступных голосов с использованием существующей логики"""
    try:
        trend_module = TrendModule()
        voices = trend_module.get_available_voices()
        
        return jsonify({
            'success': True,
            'voices': voices
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_integration_bp.route('/api/trends/avatars', methods=['GET'])
def get_avatars():
    """Получение доступных аватаров с использованием существующей логики"""
    try:
        trend_module = TrendModule()
        avatars = trend_module.get_available_avatars()
        
        return jsonify({
            'success': True,
            'avatars': avatars
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
