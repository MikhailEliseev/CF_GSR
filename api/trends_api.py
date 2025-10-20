from flask import Blueprint, request, jsonify
from models import db, TrendAnalysis, CompetitorData, ContentGeneration
import uuid
from datetime import datetime

trends_bp = Blueprint('trends', __name__)

@trends_bp.route('/api/trends/start-analysis', methods=['POST'])
def start_analysis():
    """Запуск анализа трендов"""
    try:
        data = request.get_json()
        
        # Создаем новый анализ
        analysis = TrendAnalysis(
            config=data.get('config', {}),
            status='collecting'
        )
        db.session.add(analysis)
        db.session.commit()
        
        # Запускаем фоновую задачу парсинга
        from celery_app import parse_competitors_task
        task = parse_competitors_task.delay(analysis.id)
        
        return jsonify({
            'success': True,
            'analysis_id': analysis.id,
            'task_id': task.id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_bp.route('/api/trends/analysis/<int:analysis_id>/status', methods=['GET'])
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

@trends_bp.route('/api/trends/analysis/<int:analysis_id>/competitors', methods=['GET'])
def get_competitors(analysis_id):
    """Получение списка конкурентов"""
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
                'is_selected': comp.is_selected
            })
        
        return jsonify({
            'success': True,
            'competitors': result
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_bp.route('/api/trends/analysis/<int:analysis_id>/select-post', methods=['POST'])
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

@trends_bp.route('/api/trends/transcribe', methods=['POST'])
def transcribe():
    """Запуск транскрибации"""
    try:
        data = request.get_json()
        analysis_id = data.get('analysis_id')
        
        # Находим выбранный пост
        selected_post = CompetitorData.query.filter_by(
            analysis_id=analysis_id, 
            is_selected=True
        ).first()
        
        if not selected_post:
            return jsonify({'success': False, 'error': 'No post selected'}), 400
        
        # Запускаем задачу транскрибации
        from tasks.trends import transcribe_video_task
        task = transcribe_video_task.delay(analysis_id, selected_post.id)
        
        return jsonify({
            'success': True,
            'task_id': task.id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_bp.route('/api/trends/rewrite', methods=['POST'])
def rewrite():
    """Запуск переписывания текста"""
    try:
        data = request.get_json()
        analysis_id = data.get('analysis_id')
        transcript_text = data.get('transcript_text')
        
        # Запускаем задачу переписывания
        from tasks.trends import rewrite_text_task
        task = rewrite_text_task.delay(analysis_id, transcript_text)
        
        return jsonify({
            'success': True,
            'task_id': task.id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_bp.route('/api/trends/voice/generate', methods=['POST'])
def generate_voice():
    """Генерация озвучки"""
    try:
        data = request.get_json()
        analysis_id = data.get('analysis_id')
        text = data.get('text')
        voice_settings = data.get('voice_settings', {})
        
        # Запускаем задачу генерации озвучки
        from tasks.trends import generate_voice_task
        task = generate_voice_task.delay(analysis_id, text, voice_settings)
        
        return jsonify({
            'success': True,
            'task_id': task.id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@trends_bp.route('/api/trends/video/generate', methods=['POST'])
def generate_video():
    """Генерация видео"""
    try:
        data = request.get_json()
        analysis_id = data.get('analysis_id')
        audio_file_url = data.get('audio_file_url')
        avatar_settings = data.get('avatar_settings', {})
        
        # Запускаем задачу генерации видео
        from tasks.trends import generate_video_task
        task = generate_video_task.delay(analysis_id, audio_file_url, avatar_settings)
        
        return jsonify({
            'success': True,
            'task_id': task.id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
