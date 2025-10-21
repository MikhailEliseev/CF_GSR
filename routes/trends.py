"""Blueprint с эндпоинтами модуля трендвотчинга."""
from __future__ import annotations

from flask import Blueprint, jsonify, request, render_template
from models import db, Settings, Competitors
from modules.module1_trends import TrendModule
from services import AssemblyService
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import os
import uuid
from threading import Thread

trends_bp = Blueprint('trends', __name__)

# Глобальный словарь для хранения статуса задач
task_status = {}
task_lock = threading.Lock()

# Глобальный словарь для хранения статуса задач Submagic
submagic_tasks = {}
submagic_lock = threading.Lock()


def _get_trends_settings() -> Settings | None:
    return Settings.query.filter_by(module_name='trends').first()


@trends_bp.route('/api/trends/test-video-url', methods=['GET'])
def get_test_video_url():
    """Возвращает URL тестового видео для Submagic"""
    import os
    import glob
    
    # Ищем последнее сгенерированное видео HeyGen
    video_dir = '/root/static/video'
    if os.path.exists(video_dir):
        video_files = glob.glob(os.path.join(video_dir, '*.mp4'))
        if video_files:
            # Сортируем по времени модификации, берем самое свежее
            latest_video = max(video_files, key=os.path.getmtime)
            video_filename = os.path.basename(latest_video)
            video_url = f'http://72.56.66.228/static/video/{video_filename}'
            
            # Получаем размер файла для информации
            file_size = os.path.getsize(latest_video)
            file_size_mb = round(file_size / (1024 * 1024), 1)

            return jsonify({
                'success': True,
                'video_id': f'test_video_{video_filename}',
                'video_url': video_url,
                'duration': 60.0,
                'file_size_mb': file_size_mb,
                'message': f'Реальное HeyGen видео: {video_filename} ({file_size_mb}MB)'
            })
    
    # Если не получилось - возвращаем ошибку
    return jsonify({
        'success': False,
        'message': 'Нет доступных видео для тестирования'
    }), 404


@trends_bp.route('/test-submagic')
def test_submagic_page():
    """Тестовая страница для Submagic API"""
    return render_template('test_submagic.html')


@trends_bp.route('/api/trends/upload-video', methods=['POST'])
def upload_video():
    """Загрузка видео файла на сервер"""
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'message': 'Файл не выбран'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Файл не выбран'}), 400
        
        # Проверяем тип файла
        if not file.content_type.startswith('video/'):
            return jsonify({'success': False, 'message': 'Выберите видео файл'}), 400
        
        # Проверяем размер файла (максимум 100MB)
        file.seek(0, 2)  # Переходим в конец файла
        file_size = file.tell()
        file.seek(0)  # Возвращаемся в начало
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            return jsonify({'success': False, 'message': 'Файл слишком большой. Максимум 100MB.'}), 400
        
        # Генерируем уникальное имя файла
        import uuid
        import os
        from werkzeug.utils import secure_filename
        
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Сохраняем файл
        upload_dir = '/root/static/video'
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Возвращаем URL для доступа к файлу
        video_url = f'http://72.56.66.228/static/video/{unique_filename}'
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'video_url': video_url,
            'file_size_mb': round(file_size / (1024 * 1024), 1),
            'message': f'Видео загружено: {unique_filename}'
        })
        
    except Exception as e:
        print(f"❌ Ошибка загрузки видео: {e}")
        return jsonify({
            'success': False, 
            'message': f'Ошибка загрузки: {str(e)}'
        }), 500


@trends_bp.route('/api/trends/add-captions', methods=['POST'])
def add_captions_to_video():
    """Добавление субтитров и эффектов к видео через Submagic (асинхронно)"""
    try:
        data = request.get_json() or {}
        video_url = data.get('video_url')
        settings = data.get('settings', {})
        
        if not video_url:
            return jsonify({'success': False, 'message': 'URL видео не указан'}), 400
        
        print(f"🎬 Начинаем асинхронное добавление субтитров к видео: {video_url}")
        print(f"⚙️ Настройки: {settings}")
        
        # Создаем уникальный task_id
        task_id = f"submagic_{uuid.uuid4().hex[:8]}"
        
        # Сохраняем статус задачи
        with submagic_lock:
            submagic_tasks[task_id] = {
                'status': 'processing',
                'progress': 0,
                'video_url': video_url,
                'settings': settings,
                'result_url': None,
                'error': None,
                'start_time': time.time()
            }
        
        # Запускаем обработку в фоне
        thread = Thread(target=process_submagic_async, args=(task_id, video_url, settings))
        thread.daemon = True
        thread.start()
        
        print(f"🚀 Запущена фоновая задача Submagic: {task_id}")
        
        # Немедленно возвращаем task_id и исходное видео
        return jsonify({
            'success': True,
            'task_id': task_id,
            'video_url': video_url,  # Исходное видео HeyGen
            'message': 'Обработка запущена в фоне'
        })
            
    except Exception as e:
        print(f"❌ Ошибка запуска обработки: {e}")
        return jsonify({
            'success': False, 
            'message': f'Ошибка запуска обработки: {str(e)}'
        })


def process_submagic_async(task_id, video_url, settings):
    """Фоновая обработка видео через Submagic"""
    try:
        print(f"🔄 Начинаем фоновую обработку Submagic для задачи {task_id}")
        print(f"📹 URL видео: {video_url}")
        print(f"⚙️ Настройки: {settings}")
        
        # Обновляем прогресс
        with submagic_lock:
            submagic_tasks[task_id]['progress'] = 10
        
        # Создаем контекст Flask приложения
        from app import create_app
        app, socketio = create_app()
        with app.app_context():
            print(f"🔧 Получаем настройки из базы данных...")
            
            # Получаем API ключ
            settings_db = Settings.query.filter_by(module_name='trends').first()
            if not settings_db:
                raise Exception('Настройки модуля не найдены')
            
            api_keys = settings_db.get_api_keys()
            submagic_key = api_keys.get('submagic_api_key')
            if not submagic_key:
                raise Exception('Submagic API ключ не настроен')
            
            print(f"🔑 Submagic API ключ: {submagic_key[:20]}...")
            
            # Создаем SubmagicService
            from services.submagic_service import SubmagicService
            submagic_service = SubmagicService(submagic_key)
            print(f"✅ SubmagicService создан")
            
            # Обновляем прогресс
            with submagic_lock:
                submagic_tasks[task_id]['progress'] = 20
            
            # Обрабатываем видео с callback для прогресса
            def progress_callback(progress):
                with submagic_lock:
                    submagic_tasks[task_id]['progress'] = 20 + int(progress * 0.7)  # 20-90%
                print(f"📊 Прогресс Submagic: {progress}%")
            
            print(f"🎬 Вызываем submagic_service.add_captions...")
            processed_video_path = submagic_service.add_captions(video_url, settings, progress_callback)
            print(f"✅ Submagic обработка завершена: {processed_video_path}")
            
            # Обновляем прогресс
            with submagic_lock:
                submagic_tasks[task_id]['progress'] = 90
            
            # Возвращаем URL для доступа к файлу
            result_url = f"/static/video/{os.path.basename(processed_video_path)}"
            print(f"🔗 Результат URL: {result_url}")
            
            # Завершаем задачу
            with submagic_lock:
                submagic_tasks[task_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'result_url': result_url
                })
            
            print(f"✅ Фоновая обработка Submagic завершена: {result_url}")
            
    except Exception as e:
        print(f"❌ Ошибка фоновой обработки Submagic: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        with submagic_lock:
            submagic_tasks[task_id].update({
                'status': 'error',
                'error': str(e)
            })


@trends_bp.route('/api/trends/submagic-status/<task_id>', methods=['GET'])
def get_submagic_status(task_id):
    """Получение статуса обработки Submagic"""
    with submagic_lock:
        task = submagic_tasks.get(task_id)
    
    if not task:
        return jsonify({'success': False, 'message': 'Задача не найдена'}), 404
    
    return jsonify({
        'success': True,
        'status': task['status'],  # processing, completed, error
        'progress': task['progress'],  # 0-100
        'video_url': task.get('result_url'),
        'error': task.get('error'),
        'elapsed_time': int(time.time() - task.get('start_time', time.time()))
    })


@trends_bp.route('/api/trends/submagic-templates', methods=['GET'])
def get_submagic_templates():
    """Получение списка шаблонов Submagic"""
    try:
        # Создаем модуль в контексте Flask
        from flask import current_app
        with current_app.app_context():
            # Получаем API ключ напрямую из базы данных
            settings = Settings.query.filter_by(module_name='trends').first()
            if not settings:
                return jsonify({'success': False, 'message': 'Настройки модуля не найдены'}), 500
            
            api_keys = settings.get_api_keys()
            submagic_key = api_keys.get('submagic_api_key')
            if not submagic_key:
                return jsonify({'success': False, 'message': 'Submagic API ключ не настроен'}), 500
            
            # Создаем SubmagicService напрямую
            from services.submagic_service import SubmagicService
            submagic_service = SubmagicService(submagic_key)
            
            templates = submagic_service.get_templates()
            
            return jsonify({'success': True, 'templates': templates})
            
    except Exception as e:
        print(f"❌ Ошибка получения шаблонов: {e}")
        return jsonify({'success': False, 'message': f'Ошибка получения шаблонов: {str(e)}'}), 500


@trends_bp.route('/api/trends/submagic-languages', methods=['GET'])
def get_submagic_languages():
    """Получение списка языков Submagic"""
    try:
        # Создаем модуль в контексте Flask
        from flask import current_app
        with current_app.app_context():
            # Получаем API ключ напрямую из базы данных
            settings = Settings.query.filter_by(module_name='trends').first()
            if not settings:
                return jsonify({'success': False, 'message': 'Настройки модуля не найдены'}), 500
            
            api_keys = settings.get_api_keys()
            submagic_key = api_keys.get('submagic_api_key')
            if not submagic_key:
                return jsonify({'success': False, 'message': 'Submagic API ключ не настроен'}), 500
            
            # Создаем SubmagicService напрямую
            from services.submagic_service import SubmagicService
            submagic_service = SubmagicService(submagic_key)
            
            languages = submagic_service.get_languages()
            
            return jsonify({'success': True, 'languages': languages})
            
    except Exception as e:
        print(f"❌ Ошибка получения языков: {e}")
        return jsonify({'success': False, 'message': f'Ошибка получения языков: {str(e)}'}), 500


@trends_bp.route('/api/trends/start-step-generation', methods=['POST'])
def start_step_generation():
    """Запуск пошаговой генерации"""
    try:
        data = request.get_json() or {}
        step = data.get('step')
        task_id = data.get('task_id')
        
        if not step or not task_id:
            return jsonify({'success': False, 'message': 'Step and task_id required'}), 400
        
        # Запускаем задачу в фоне
        from celery_app import celery_app
        task = celery_app.send_task(
            'modules.module1_trends.TrendModule.start_step_by_step_generation',
            args=[task_id, step],
            kwargs=data.get('kwargs', {})
        )
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': f'Шаг {step} запущен'
        })
        
    except Exception as e:
        print(f"❌ Ошибка запуска шага: {e}")
        return jsonify({'success': False, 'message': f'Ошибка запуска шага: {str(e)}'}), 500


@trends_bp.route('/api/trends/collect-reels', methods=['POST'])
def collect_reels():
    """Сбор рилсов конкурентов через Apify"""
    data = request.get_json() or {}
    competitors = data.get('competitors', [])
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
    """Транскрибация видео через AssemblyAI"""
    data = request.get_json() or {}
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({'success': False, 'message': 'URL видео не передан'}), 400

    settings = _get_trends_settings()
    api_keys = settings.get_api_keys() if settings else {}
    assembly_service = AssemblyService(api_keys.get('assemblyai_api_key'))
    transcript = assembly_service.transcribe(video_url)

    return jsonify({'success': True, 'transcript': transcript})


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
    """Генерация аудио через ElevenLabs"""
    data = request.get_json() or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'success': False, 'message': 'Текст для озвучки не передан'}), 400

    module = TrendModule()
    additional = module.settings.get_additional_settings() or {}

    voice_id = data.get('voice_id') or additional.get('default_voice_id') or 'demo_voice'
    model_id = data.get('model_id') or additional.get('default_voice_model')

    audio_url = module.elevenlabs_service.generate_audio(text, voice_id=voice_id, model_id=model_id)

    payload = {'success': True, 'audio_url': audio_url}
    if not module.elevenlabs_service.api_key:
        payload['warning'] = 'ElevenLabs API ключ не настроен, используется демо-аудио'
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
