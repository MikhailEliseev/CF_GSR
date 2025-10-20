"""Blueprint с эндпоинтами модуля трендвотчинга."""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from models import db, Settings, Competitors
from modules.module1_trends import TrendModule
from services import AssemblyService
from typing import List, Dict, Any

trends_bp = Blueprint('trends', __name__)


def _get_trends_settings() -> Settings | None:
    return Settings.query.filter_by(module_name='trends').first()


@trends_bp.route('/api/trends/collect-reels', methods=['POST'])
def collect_reels():
    """Сбор рилсов конкурентов через Apify"""
    data = request.get_json() or {}
    competitors: List[str] = data.get('competitors', [])
    count = int(data.get('count', 10) or 10)

    if not competitors:
        return jsonify({'success': False, 'message': 'Не выбраны конкуренты для сбора'}), 400

    module = TrendModule()
    reels = module.apify_service.fetch_reels(competitors, count)

    if not reels:
        return jsonify({'success': False, 'message': 'Apify не вернул данные. Проверьте API ключ и список конкурентов.'}), 400

    viral = [post for post in reels if post.get('is_viral') or (post.get('views_count') or 0) > 30000]

    return jsonify({
        'success': True,
        'reels': reels,
        'total_count': len(reels),
        'viral_count': len(viral)
    })


@trends_bp.route('/api/trends/transcribe', methods=['POST'])
def transcribe_reel():
    """Транскрибация видео через AssemblyAI с увеличенным таймаутом"""
    data = request.get_json() or {}
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({'success': False, 'message': 'URL видео не передан'}), 400

    try:
        settings = _get_trends_settings()
        api_keys = settings.get_api_keys() if settings else {}
        assembly_service = AssemblyService(api_keys.get('assemblyai_api_key'))
        
        print(f"🎤 Начинаем транскрибацию: {video_url[:50]}...")
        transcript = assembly_service.transcribe(video_url)
        print(f"✅ Транскрибация завершена: {len(transcript)} символов")

        return jsonify({'success': True, 'transcript': transcript})
        
    except Exception as e:
        print(f"❌ Ошибка транскрибации: {e}")
        return jsonify({
            'success': False, 
            'message': f'Ошибка транскрибации: {str(e)}. Попробуйте еще раз или проверьте URL видео.'
        }), 500


@trends_bp.route('/api/trends/rewrite', methods=['POST'])
def rewrite_text():
    """Переписывание текста через OpenAI"""
    data = request.get_json() or {}
    transcript = (data.get('transcript') or '').strip()

    if not transcript:
        return jsonify({'success': False, 'message': 'Текст транскрипции не передан'}), 400

    module = TrendModule()
    rewritten = module.openai_service.rewrite_transcript(
        transcript,
        master_prompt=module.settings.master_prompt
    )

    return jsonify({'success': True, 'rewritten_text': rewritten})


@trends_bp.route('/api/trends/generate-audio', methods=['POST'])
def generate_audio():
    """Генерация аудио через ElevenLabs с полными настройками"""
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"success": False, "message": "Текст для озвучки не передан"}), 400

    module = TrendModule()
    additional = module.settings.get_additional_settings() or {}

    # Получаем все настройки голоса
    voice_id = data.get("voice_id") or additional.get("default_voice_id") or "jP9L6ZC55cz5mmx4ZpCk"
    model_id = data.get("model_id") or additional.get("default_voice_model") or "eleven_flash_v2_5"
    speed = float(data.get("speed", 1.0))
    stability = float(data.get("stability", 0.5))
    similarity_boost = float(data.get("similarity_boost", 0.5))

    # Используем новый метод с полными настройками
    audio_url = module.elevenlabs_service.generate_audio_advanced(
        text, voice_id=voice_id, model_id=model_id, 
        speed=speed, stability=stability, similarity_boost=similarity_boost
    )

    payload = {"success": True, "audio_url": audio_url}
    if not module.elevenlabs_service.api_key:
        payload["warning"] = "ElevenLabs API ключ не настроен, используется демо-аудио"
    return jsonify(payload)


@trends_bp.route('/api/trends/generate-video', methods=['POST'])
def generate_video():
    """Создание видео через HeyGen"""
    data = request.get_json() or {}
    audio_url = (data.get('audio_url') or '').strip()
    avatar_id = data.get('avatar_id') or 'demo_avatar'

    if not audio_url:
        return jsonify({'success': False, 'message': 'Аудио не передано'}), 400

    module = TrendModule()
    video_info = module.heygen_service.generate_video(audio_url, avatar_id)

    payload: Dict[str, Any] = {'success': True}
    payload.update(video_info if isinstance(video_info, dict) else {'video_url': video_info})

    if not module.heygen_service.api_key:
        payload['warning'] = 'HeyGen API ключ не настроен, используется демо-видео'
    return jsonify(payload)


@trends_bp.route('/api/trends/voices', methods=['GET'])
def list_voices():
    """Получение списка голосов"""
    module = TrendModule()
    voices = module.elevenlabs_service.list_voices() if module.elevenlabs_service else []
    return jsonify({'success': True, 'voices': voices})


@trends_bp.route('/api/trends/avatars', methods=['GET'])
def list_avatars():
    """Получение списка аватаров"""
    module = TrendModule()
    avatars = module.heygen_service.list_avatars() if module.heygen_service else []
    return jsonify({'success': True, 'avatars': avatars})


@trends_bp.route('/api/competitors', methods=['GET', 'POST', 'DELETE'])
def manage_competitors():
    """Управление конкурентами"""
    if request.method == 'GET':
        competitors = Competitors.query.filter_by(is_active=True).all()
        return jsonify([
            {
                'id': c.id,
                'username': c.username,
                'platform': c.platform,
                'last_checked': c.last_checked.isoformat() if c.last_checked else None
            }
            for c in competitors
        ])

    if request.method == 'POST':
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        platform = data.get('platform', 'instagram')
        if not username:
            return jsonify({'success': False, 'message': 'Username is required'}), 400

        competitor = Competitors(username=username, platform=platform)
        db.session.add(competitor)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Конкурент добавлен'})

    competitor_id = request.args.get('id')
    competitor = Competitors.query.get(competitor_id)
    if competitor:
        competitor.is_active = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Конкурент удален'})
    return jsonify({'success': False, 'message': 'Конкурент не найден'}), 404
