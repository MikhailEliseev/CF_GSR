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
        from app_current_backup import create_app
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
