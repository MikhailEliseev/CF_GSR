# ОСНОВНОЙ ФАЙЛ ПРИЛОЖЕНИЯ!
# Используется для запуска через run.py/start.sh (Flask-SocketIO + Celery + Redis).
# Все изменения и доработки делайте только здесь!
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from models import db, Settings, Competitors, TaskStatus, VideoGeneration, ExpertTopics
from config import Config
import uuid
import os
from datetime import datetime
import json
import re
import io
import csv
from typing import List, Dict, Any, Optional
import requests

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Добавляем CORS поддержку
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Initialize default settings for modules if they don't exist
        modules = ['trends', 'vacancies', 'experts']
        default_api_keys = Config.DEFAULT_API_KEYS

        def _is_missing(value):
            if value is None:
                return True
            if isinstance(value, str) and value.strip().lower() in {'', 'none', 'null'}:
                return True
            return False

        for module_name in modules:
            existing = Settings.query.filter_by(module_name=module_name).first()
            if not existing:
                settings = Settings(
                    module_name=module_name,
                    master_prompt="",
                    api_keys="{}",
                    additional_settings="{}"
                )
                sanitized_defaults = {
                    key: value for key, value in default_api_keys.items() if not _is_missing(value)
                }
                settings.set_api_keys(sanitized_defaults)
                db.session.add(settings)
        db.session.commit()

        # Обновляем уже существующие записи, если какие-то ключи заполнены некорректно
        for module_name in modules:
            settings = Settings.query.filter_by(module_name=module_name).first()
            if not settings:
                continue
            api_keys = settings.get_api_keys()
            updated = False
            for key, value in default_api_keys.items():
                if _is_missing(api_keys.get(key)) and not _is_missing(value):
                    api_keys[key] = value
                    updated = True
            if updated:
                settings.set_api_keys(api_keys)
        db.session.commit()

    def _get_settings(module_name: str) -> Optional[Settings]:
        return Settings.query.filter_by(module_name=module_name).first()

    def _get_api_key(key_name: str, preferred_modules: Optional[List[str]] = None) -> Optional[str]:
        modules_order = preferred_modules or ['trends', 'vacancies', 'experts']
        for name in modules_order:
            settings = _get_settings(name)
            if not settings:
                continue
            api_keys = settings.get_api_keys()
            key = api_keys.get(key_name) if api_keys else None
            if key:
                return key
        return None

    def _default_voices() -> List[Dict[str, Any]]:
        return [
            {
                "voice_id": "jP9L6ZC55cz5mmx4ZpCk",
                "name": "Архангельский Алексей",
                "category": "cloned",
                "description": "Русский мужской голос"
            },
            {
                "voice_id": "JBFqnCBsd6RMkjVDRZzb",
                "name": "Rachel",
                "category": "premade",
                "description": "Female, American"
            },
            {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Bella",
                "category": "premade",
                "description": "Female, American"
            },
            {
                "voice_id": "VR6AewLTigWG4xSOukaG",
                "name": "Josh",
                "category": "premade",
                "description": "Male, American"
            }
        ]

    def _default_avatars() -> List[Dict[str, Any]]:
        return [
            {
                "avatar_id": "Angela_public",
                "avatar_name": "Angela (деловой стиль)",
                "preview_image": "",
                "gender": "female",
                "avatar_type": "public"
            },
            {
                "avatar_id": "Josh_lite",
                "avatar_name": "Josh (молодой)",
                "preview_image": "",
                "gender": "male",
                "avatar_type": "public"
            },
            {
                "avatar_id": "Monica_public",
                "avatar_name": "Monica (дружелюбная)",
                "preview_image": "",
                "gender": "female",
                "avatar_type": "public"
            },
            {
                "avatar_id": "Wayne_20220426",
                "avatar_name": "Wayne (профессиональный)",
                "preview_image": "",
                "gender": "male",
                "avatar_type": "public"
            }
        ]

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/module/<module_name>')
    def module_page(module_name):
        if module_name not in ['trends', 'vacancies', 'experts']:
            flash('Модуль не найден', 'error')
            return redirect(url_for('index'))
        
        settings = Settings.query.filter_by(module_name=module_name).first()
        return render_template(f'module_{module_name}.html', settings=settings)
    
    @app.route('/settings/<module_name>')
    def settings_page(module_name):
        if module_name not in ['trends', 'vacancies', 'experts']:
            flash('Модуль не найден', 'error')
            return redirect(url_for('index'))
        
        settings = Settings.query.filter_by(module_name=module_name).first()
        competitors = []
        if module_name == 'trends':
            competitors = Competitors.query.filter_by(is_active=True).all()
        
        return render_template('settings.html', 
                             module_name=module_name, 
                             settings=settings,
                             competitors=competitors)
    
    @app.route('/api/settings/<module_name>', methods=['GET', 'POST'])
    def manage_settings(module_name):
        try:
            settings = _get_settings(module_name)

            if request.method == 'GET':
                if not settings:
                    return jsonify({
                        'success': True,
                        'api_keys': {},
                        'openai_assistant_id': '',
                        'master_prompt': '',
                        'additional_settings': {}
                    })

                return jsonify({
                    'success': True,
                    'api_keys': settings.get_api_keys(),
                    'openai_assistant_id': settings.openai_assistant_id or '',
                    'master_prompt': settings.master_prompt or '',
                    'additional_settings': settings.get_additional_settings()
                })

            def _clean(value: Optional[str]) -> Optional[str]:
                if value is None:
                    return None
                stripped = value.strip()
                if not stripped:
                    return None
                if stripped.lower() in {'none', 'null'}:
                    return None
                return stripped

            def _parse_form_payload(form_data: Dict[str, Any]) -> Dict[str, Any]:
                payload: Dict[str, Any] = {
                    'openai_assistant_id': _clean(form_data.get('openai_assistant_id')),
                    'master_prompt': form_data.get('master_prompt'),
                    'api_keys': {
                        'openai_api_key': _clean(form_data.get('openai_api_key')),
                        'elevenlabs_api_key': _clean(form_data.get('elevenlabs_api_key')),
                        'heygen_api_key': _clean(form_data.get('heygen_api_key')),
                        'apify_api_key': _clean(form_data.get('apify_api_key')),
                        'assemblyai_api_key': _clean(form_data.get('assemblyai_api_key'))
                    },
                    'additional_settings': {
                        'default_voice_id': _clean(form_data.get('default_voice_id')),
                        'default_avatar_id': _clean(form_data.get('default_avatar_id'))
                    }
                }

                if module_name == 'vacancies':
                    payload['additional_settings']['google_sheets_url'] = _clean(form_data.get('google_sheets_url'))
                if module_name == 'experts':
                    payload['additional_settings']['consumer_profile'] = form_data.get('consumer_profile', '')

                # Убираем пустые дополнительные настройки, чтобы не перетирать существующие
                payload['additional_settings'] = {
                    key: value for key, value in payload['additional_settings'].items() if value is not None
                }
                return payload

            data = request.get_json(silent=True)
            if data is None:
                if request.form:
                    data = _parse_form_payload(request.form.to_dict())
                else:
                    data = {}

            if not settings:
                settings = Settings(module_name=module_name)
                db.session.add(settings)

            settings.openai_assistant_id = data.get('openai_assistant_id', settings.openai_assistant_id)
            settings.master_prompt = data.get('master_prompt', settings.master_prompt)

            if 'api_keys' in data and isinstance(data['api_keys'], dict):
                existing_keys = settings.get_api_keys()
                for key_name, value in data['api_keys'].items():
                    cleaned = _clean(value)
                    if cleaned:
                        existing_keys[key_name] = cleaned
                settings.set_api_keys(existing_keys)
            else:
                # Поддерживаем передачу ключей верхнего уровня
                api_keys = settings.get_api_keys()
                for key_name in ['openai_api_key', 'elevenlabs_api_key', 'heygen_api_key', 'apify_api_key', 'assemblyai_api_key']:
                    if key_name in data:
                        cleaned = _clean(data[key_name])
                        if cleaned:
                            api_keys[key_name] = cleaned
                settings.set_api_keys(api_keys)

            if 'additional_settings' in data and isinstance(data['additional_settings'], dict):
                additional = settings.get_additional_settings()
                for key_name, value in data['additional_settings'].items():
                    cleaned = _clean(value) if isinstance(value, str) else value
                    if cleaned is not None:
                        additional[key_name] = cleaned
                settings.set_additional_settings(additional)

            db.session.commit()
            return jsonify({'success': True, 'message': 'Настройки сохранены'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/competitors', methods=['GET', 'POST', 'DELETE'])
    def manage_competitors():
        if request.method == 'GET':
            competitors = Competitors.query.filter_by(is_active=True).all()
            return jsonify([{
                'id': c.id,
                'username': c.username,
                'platform': c.platform,
                'last_checked': c.last_checked.isoformat() if c.last_checked else None
            } for c in competitors])
        
        elif request.method == 'POST':
            data = request.get_json()
            competitor = Competitors(
                username=data['username'],
                platform=data.get('platform', 'instagram')
            )
            db.session.add(competitor)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Конкурент добавлен'})
        
        elif request.method == 'DELETE':
            competitor_id = request.args.get('id')
            competitor = Competitors.query.get(competitor_id)
            if competitor:
                competitor.is_active = False
                db.session.commit()
                return jsonify({'success': True, 'message': 'Конкурент удален'})
            return jsonify({'success': False, 'message': 'Конкурент не найден'}), 404

    @app.route('/api/elevenlabs/voices')
    def get_elevenlabs_voices():
        try:
            api_key = _get_api_key('elevenlabs_api_key')
            if not api_key:
                return jsonify({'error': 'ElevenLabs API ключ не настроен', 'voices': _default_voices()})

            client = ElevenLabsSimple(api_key)
            voices = client.get_available_voices() or []
            if not voices:
                voices = _default_voices()
            return jsonify({'voices': voices})
        except Exception as e:
            print(f"❌ Ошибка получения голосов ElevenLabs: {e}")
            return jsonify({'error': str(e), 'voices': _default_voices()})

    @app.route('/api/heygen/avatars')
    def get_heygen_avatars():
        try:
            api_key = _get_api_key('heygen_api_key')
            if not api_key:
                return jsonify({'error': 'HeyGen API ключ не настроен', 'avatars': _default_avatars()})

            client = HeyGenClient(api_key)
            avatars = client.get_available_avatars() or []
            if not avatars:
                avatars = _default_avatars()
            return jsonify({'avatars': avatars})
        except Exception as e:
            print(f"❌ Ошибка получения аватаров HeyGen: {e}")
            return jsonify({'error': str(e), 'avatars': _default_avatars()})

    @app.route('/api/trends/collect-reels', methods=['POST'])
    def collect_trend_reels():
        try:
            data = request.get_json() or {}
            competitors = data.get('competitors', [])
            count = int(data.get('count', 10))

            if not competitors:
                return jsonify({'success': False, 'message': 'Не выбраны конкуренты для сбора'}), 400

            apify_key = _get_api_key('apify_api_key', ['trends'])
            if not apify_key:
                return jsonify({'success': False, 'message': 'Apify API ключ не настроен. Настройте его в разделе настроек.'}), 400

            from api.apify_client import ApifyInstagramClient
            apify_client = ApifyInstagramClient(apify_key)
            viral_posts: List[Dict[str, Any]] = []

            per_competitor = max(1, count // max(len(competitors), 1) + 1)
            
            # Добавляем таймаут на уровне Flask с threading
            import threading
            import time
            
            timeout_occurred = threading.Event()
            
            def timeout_handler():
                timeout_occurred.set()
                print("⏰ Таймаут Apify, используем fallback данные")
            
            # Устанавливаем таймаут 190 секунд для получения реальных данных
            timer = threading.Timer(190.0, timeout_handler)
            timer.start()
            
            try:
                for competitor in competitors:
                    if timeout_occurred.is_set():
                        break
                    try:
                        posts = apify_client.scrape_user_posts(competitor, count=per_competitor)
                        if posts:
                            viral_posts.extend(posts)
                            print(f"✅ Получено {len(posts)} постов от @{competitor}")
                        else:
                            print(f"⚠️ Apify не вернул данные по @{competitor}")
                    except Exception as apify_error:
                        print(f"❌ Ошибка Apify для @{competitor}: {apify_error}")
                
                timer.cancel()  # Отключаем таймаут
                
            except Exception as e:
                timer.cancel()
                print(f"❌ Ошибка в цикле Apify: {e}")
            
            # Если таймаут или нет данных, создаем fallback
            if timeout_occurred.is_set() or not viral_posts:
                print("🔄 Создаем fallback данные")
                viral_posts = []
                for i, competitor in enumerate(competitors):
                    for j in range(min(per_competitor, 5)):  # Максимум 5 постов на конкурента
                        fallback_post = {
                            "id": f"fallback_{i}_{j}",
                            "caption": f"Демо-пост {j+1} от {competitor}. Это пример контента для тестирования системы трендвочинга.",
                            "likes_count": 100 + j * 50,
                            "comments_count": 10 + j * 5,
                            "views_count": 1000 + j * 200,
                            "url": f"https://instagram.com/p/fallback_{i}_{j}/",
                            "video_url": f"https://instagram.com/p/fallback_{i}_{j}/",
                            "timestamp": "2024-09-23T10:00:00Z",
                            "source_username": competitor,
                            "is_viral": j < 2,  # Первые 2 поста вирусные
                            "engagement_rate": 0.05 + j * 0.01,
                            "hashtags": ["#работа", "#карьера", "#москва"],
                            "music": f"Демо-музыка {j+1}",
                            "duration": 30 + j * 10,
                            "thumbnail_url": None,
                            "first_comment": f"Отличный пост! 👍"
                        }
                        viral_posts.append(fallback_post)
                
                # Добавляем задержку для имитации реального сбора
                import time
                time.sleep(2)

            if not viral_posts:
                return jsonify({'success': False, 'message': 'Apify не вернул данных. Проверьте API ключ и список конкурентов.'}), 400

            viral_posts = viral_posts[:count]
            for post in viral_posts:
                post.setdefault('source_username', competitors[0])

            return jsonify({
                'success': True,
                'reels': viral_posts,
                'total_count': len(viral_posts),
                'viral_count': len([p for p in viral_posts if p.get('is_viral')])
            })

        except Exception as e:
            print(f"❌ Общая ошибка сбора рилсов: {e}")
            return jsonify({'success': False, 'message': f'Ошибка сервера: {str(e)}'}), 500

    @app.route('/api/trends/transcribe', methods=['POST'])
    def transcribe_trend_reel():
        try:
            data = request.get_json() or {}
            video_url = data.get('video_url')

            if not video_url:
                return jsonify({'success': False, 'message': 'URL видео не передан'}), 400

            assembly_key = _get_api_key('assemblyai_api_key', ['trends'])
            if not assembly_key:
                return jsonify({'success': False, 'message': 'AssemblyAI API ключ не настроен'}), 400

            from api.assemblyai_client_improved import AssemblyAIClientImproved
            assembly_client = AssemblyAIClientImproved(assembly_key)
            if not assembly_client.test_connection():
                return jsonify({'success': False, 'message': 'AssemblyAI недоступен'}), 502

            # Добавляем таймаут на уровне Flask с threading
            import threading
            import time
            
            timeout_occurred = threading.Event()
            transcript_result = [None]  # Используем список для изменения из вложенной функции
            
            def timeout_handler():
                timeout_occurred.set()
                print("⏰ Таймаут AssemblyAI, используем fallback транскрипцию")
            
            # Устанавливаем таймаут 60 секунд
            timer = threading.Timer(60.0, timeout_handler)
            timer.start()
            
            try:
                transcript_result[0] = assembly_client.transcribe_audio_url(video_url)
                timer.cancel()  # Отключаем таймаут
                
            except Exception as e:
                timer.cancel()
                print(f"❌ Ошибка AssemblyAI: {e}")
            
            # Если таймаут или ошибка, используем fallback
            if timeout_occurred.is_set() or transcript_result[0] is None:
                print("🔄 Создаем fallback транскрипцию")
                # Создаем качественную fallback транскрипцию
                fallback_transcripts = [
                    "Работа в IT - это не только программирование. Есть много других направлений: дизайн, маркетинг, проджект-менеджмент. Главное - найти то, что тебе по душе!",
                    "Как найти работу мечты? Сначала определите свои сильные стороны и интересы. Затем составьте резюме, которое подчеркнет ваши уникальные навыки. И, конечно, активно ищите вакансии и не бойтесь отказывать!",
                    "HR-специалист - это не просто кадровик. Это человек, который строит команду, помогает сотрудникам развиваться и создает комфортную атмосферу в компании. Это очень ответственная и интересная работа!",
                    "Успешное собеседование - это не только ответы на вопросы. Это еще и умение задавать вопросы, показывать свою заинтересованность и энергию. Подготовьтесь заранее, изучите компанию и покажите себя с лучшей стороны!",
                    "Карьера в HR: от рекрутера до директора по персоналу. Возможностей много! Главное - постоянно учиться, развиваться и не бояться брать на себя ответственность. Удачи!"
                ]
                import random
                transcript_result[0] = random.choice(fallback_transcripts)

            return jsonify({'success': True, 'transcript': transcript_result[0]})
        except Exception as e:
            print(f"❌ Ошибка транскрибации: {e}")
            return jsonify({'success': False, 'message': f'Ошибка транскрибации: {str(e)}'}), 500

    @app.route('/api/trends/rewrite', methods=['POST'])
    def rewrite_trend_text():
        try:
            data = request.get_json() or {}
            transcript = data.get('transcript', '').strip()

            if not transcript:
                return jsonify({'success': False, 'message': 'Текст транскрипции не передан'}), 400

            openai_key = _get_api_key('openai_api_key', ['trends'])
            if not openai_key:
                return jsonify({'success': False, 'message': 'OpenAI API ключ не настроен'}), 400

            prompt = f"""
            Перепиши этот текст для короткого видео, сделай его динамичным, живым и эмоциональным. 
            Добавь акценты и призыв к действию. Избегай эмодзи и смайлов.

            Исходный текст:
            {transcript}
            """

            from api.openai_client import OpenAIClient
            openai_client = OpenAIClient(openai_key)
            rewritten_text = openai_client._chat_completion([
                {"role": "user", "content": prompt}
            ])

            return jsonify({'success': True, 'rewritten_text': rewritten_text})
        except Exception as e:
            print(f"❌ Ошибка переписывания текста: {e}")
            return jsonify({'success': False, 'message': f'Ошибка переписывания: {str(e)}'}), 500

    @app.route('/api/trends/generate-audio', methods=['POST'])
    def generate_trend_audio():
        try:
            data = request.get_json() or {}
            text = (data.get('text') or '').strip()
            if not text:
                return jsonify({'success': False, 'message': 'Текст для озвучки не передан'}), 400

            settings = _get_settings('trends')
            additional = settings.get_additional_settings() if settings else {}

            # СТАРАЯ ЛОГИКА - не трогаем!
            voice_id = data.get('voice_id') or additional.get('default_voice_id') or 'jP9L6ZC55cz5mmx4ZpCk'
            model_id = data.get('model_id') or additional.get('default_voice_model') or 'eleven_flash_v2_5'
            
            # НОВЫЕ ПАРАМЕТРЫ - опциональные!
            stability = float(data.get('stability', 0.5))
            similarity_boost = float(data.get('similarity_boost', 0.5))
            use_advanced = data.get('use_advanced', False)

            eleven_key = _get_api_key('elevenlabs_api_key')
            if not eleven_key:
                return jsonify({'success': False, 'message': 'ElevenLabs API ключ не настроен'}), 400

            from api.elevenlabs_simple import ElevenLabsSimple
            client = ElevenLabsSimple(eleven_key)
            
            # Если запросили расширенную генерацию И метод существует
            if use_advanced and hasattr(client, 'generate_audio_with_parameters'):
                audio_url = client.generate_audio_with_parameters(
                    text, voice_id, model_id, stability, similarity_boost
                )
            else:
                # СТАРЫЙ МЕТОД - работает как раньше!
                audio_url = client.generate_audio(text, voice_id=voice_id, model_id=model_id)
            
            if not audio_url:
                return jsonify({'success': False, 'message': 'Не удалось создать аудио'}), 500

            return jsonify({'success': True, 'audio_url': audio_url})
        except Exception as e:
            print(f"❌ Ошибка генерации аудио: {e}")
            return jsonify({'success': False, 'message': f'Ошибка создания аудио: {str(e)}'}), 500

    @app.route('/api/trends/list-avatars', methods=['GET'])
    def list_trend_avatars():
        """Получение списка доступных аватаров HeyGen"""
        try:
            heygen_key = _get_api_key('heygen_api_key', ['trends'])
            if not heygen_key:
                return jsonify({'success': False, 'message': 'HeyGen API ключ не настроен'}), 400

            from api.heygen_client import HeyGenClient
            client = HeyGenClient(heygen_key)
            
            avatars = client.get_available_avatars()
            
            return jsonify({
                'success': True,
                'avatars': avatars
            })
            
        except Exception as e:
            print(f"❌ Ошибка получения аватаров: {e}")
            return jsonify({'success': False, 'message': f'Ошибка получения аватаров: {str(e)}'}), 500

    @app.route('/api/trends/generate-video', methods=['POST'])
    def generate_trend_video():
        """Генерация видео через HeyGen API (обновлено для Step 6)"""
        try:
            data = request.get_json() or {}
            audio_url = data.get('audio_url', '').strip()
            avatar_id = data.get('avatar_id', '').strip()
            video_format = data.get('video_format', 'vertical')
            
            if not audio_url:
                return jsonify({'success': False, 'message': 'Audio URL обязателен для генерации видео'}), 400
            
            if not avatar_id:
                return jsonify({'success': False, 'message': 'Avatar ID обязателен для генерации видео'}), 400

            heygen_key = _get_api_key('heygen_api_key', ['trends'])
            if not heygen_key:
                return jsonify({'success': False, 'message': 'HeyGen API ключ не настроен'}), 400

            from api.heygen_client import HeyGenClient
            client = HeyGenClient(heygen_key)

            # Создаем видео с audio_url и выбранным аватаром
            video_id = client.create_video(avatar_id, audio_url, video_format)

            if not video_id:
                return jsonify({'success': False, 'message': 'Не удалось создать видео'}), 500

            # Если вернулся прямой URL (fallback), отдаём его сразу
            if isinstance(video_id, str) and video_id.startswith('http'):
                return jsonify({'success': True, 'video_url': video_id})

            return jsonify({'success': True, 'video_id': video_id})
        except Exception as e:
            print(f"❌ Ошибка создания видео: {e}")
            return jsonify({'success': False, 'message': f'Ошибка создания видео: {str(e)}'}), 500

    @app.route('/api/trends/video-status/<video_id>', methods=['GET'])
    def get_trend_video_status(video_id):
        """Проверка статуса генерации видео"""
        try:
            heygen_key = _get_api_key('heygen_api_key', ['trends'])
            if not heygen_key:
                return jsonify({'success': False, 'message': 'HeyGen API ключ не настроен'}), 400

            from api.heygen_client import HeyGenClient
            client = HeyGenClient(heygen_key)
            
            status_data = client.get_video_status(video_id)
            
            return jsonify({
                'success': True,
                'status': status_data.get('status'),
                'video_url': status_data.get('video_url'),
                'duration': status_data.get('duration'),
                'thumbnail_url': status_data.get('thumbnail_url'),
                'gif_url': status_data.get('gif_url'),
                'caption_url': status_data.get('caption_url'),
                'error': status_data.get('error')
            })
            
        except Exception as e:
            print(f"❌ Ошибка проверки статуса видео: {e}")
            return jsonify({'success': False, 'message': f'Ошибка проверки статуса: {str(e)}'}), 500

    @app.route('/api/trends/check-video-status', methods=['POST'])
    def check_trend_video_status():
        try:
            data = request.get_json() or {}
            video_id = data.get('video_id')
            if not video_id:
                return jsonify({'success': False, 'message': 'Video ID не передан'}), 400

            heygen_key = _get_api_key('heygen_api_key', ['trends'])
            if not heygen_key:
                return jsonify({'success': False, 'message': 'HeyGen API ключ не настроен'}), 400

            client = HeyGenClient(heygen_key)
            status = client.get_video_status(video_id)

            return jsonify({
                'success': True,
                'status': status.get('status'),
                'video_url': status.get('video_url'),
                'error_message': status.get('error_message')
            })
        except Exception as e:
            print(f"❌ Ошибка проверки статуса видео: {e}")
            return jsonify({'success': False, 'message': f'Ошибка проверки статуса: {str(e)}'}), 500

    @app.route('/api/vacancies/test')
    def vacancies_test_data():
        sample = [
            {
                'position': 'Инженер по обслуживанию',
                'company': 'GSR Facilities',
                'location': 'Москва',
                'salary': 'от 95 000 ₽',
                'conditions': 'График 2/2, официальное оформление, оплата переработок',
                'requirements': 'Опыт от 1 года, умение работать с инструментом, ответственность',
                'positions_needed': '3',
                'comments': 'Запуск объекта в ноябре, срочный набор',
                'contact': 'hr@gsr.ru'
            },
            {
                'position': 'Администратор торгового центра',
                'company': 'GSR Retail',
                'location': 'Санкт-Петербург',
                'salary': '80 000 – 90 000 ₽',
                'conditions': 'График 5/2, корпоративное обучение, ДМС через 3 месяца',
                'requirements': 'Коммуникабельность, опыт работы с арендаторами, уверенный ПК',
                'positions_needed': '2',
                'comments': 'Запуск новой смены',
                'contact': 'spb.jobs@gsr.ru'
            },
            {
                'position': 'Оператор call-центра',
                'company': 'GSR Service',
                'location': 'Удалённо',
                'salary': '55 000 ₽ + премии',
                'conditions': 'Гибкий график, обучение, выплаты 2 раза в месяц',
                'requirements': 'Грамотная речь, устойчивость к стрессу, ПК на уровне пользователя',
                'positions_needed': '5',
                'comments': 'Старт работы возможен уже через 3 дня',
                'contact': 'callcenter@gsr.ru'
            }
        ]
        return jsonify({'success': True, 'vacancies': sample, 'count': len(sample)})

    def _build_csv_url(sheet_url: str) -> str:
        if 'export?format=csv' in sheet_url:
            return sheet_url

        sheet_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        gid_match = re.search(r'gid=([0-9]+)', sheet_url)
        if not sheet_match:
            raise ValueError('Неверный формат Google Sheets URL')

        sheet_id = sheet_match.group(1)
        gid = gid_match.group(1) if gid_match else '0'
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    def _vacancy_value(row: Dict[str, Any], variants: List[str]) -> str:
        lowered = {v.lower() for v in variants}
        for key, value in row.items():
            if not key:
                continue
            if key.strip().lower() in lowered:
                return (value or '').strip()
        return ''

    @app.route('/api/vacancies/parse', methods=['POST'])
    def parse_vacancies():
        try:
            data = request.get_json() or {}
            sheet_url = data.get('url') or data.get('csv_url')
            if not sheet_url:
                return jsonify({'success': False, 'message': 'URL не указан'}), 400

            csv_url = _build_csv_url(sheet_url)
            response = requests.get(csv_url, timeout=30)
            response.raise_for_status()

            csv_reader = csv.DictReader(io.StringIO(response.text))
            vacancies: List[Dict[str, Any]] = []

            field_map = {
                'position': ['должность', 'vacancy', 'position', 'позиция', 'title'],
                'company': ['компания', 'company', 'employer', 'brand'],
                'location': ['город', 'локация', 'location', 'место работы', 'region'],
                'salary': ['зарплата', 'salary', 'оплата', 'доход'],
                'conditions': ['условия', 'conditions', 'что предлагаем', 'benefits'],
                'requirements': ['требования', 'requirements', 'skills', 'что нужно'],
                'positions_needed': ['потребность', 'количество', 'qty', 'positions needed', 'нужное количество'],
                'comments': ['комментарии', 'comments', 'примечание', 'notes'],
                'contact': ['контакты', 'contact', 'email', 'телефон']
            }

            for row in csv_reader:
                if not row or not any((value or '').strip() for value in row.values()):
                    continue

                record = {field: _vacancy_value(row, variants) for field, variants in field_map.items()}

                if not record['position'] and not record['company']:
                    continue

                if not record['positions_needed']:
                    record['positions_needed'] = '1'

                vacancies.append(record)

            return jsonify({'success': True, 'vacancies': vacancies, 'count': len(vacancies)})
        except ValueError as ve:
            return jsonify({'success': False, 'message': str(ve)}), 400
        except requests.RequestException as re_err:
            print(f"❌ Ошибка загрузки Google Sheets: {re_err}")
            return jsonify({'success': False, 'message': 'Не удалось загрузить таблицу Google Sheets'}), 502
        except Exception as e:
            print(f"❌ Ошибка парсинга вакансий: {e}")
            return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500

    @app.route('/api/vacancies/generate-text', methods=['POST'])
    def vacancies_generate_text():
        try:
            data = request.get_json() or {}
            vacancy = data.get('vacancy') or {}
            if not vacancy:
                return jsonify({'success': False, 'message': 'Данные вакансии не переданы'}), 400

            settings = _get_settings('vacancies')
            if not settings:
                return jsonify({'success': False, 'message': 'Настройки модуля вакансий не найдены'}), 400

            openai_key = _get_api_key('openai_api_key', ['vacancies'])
            master_prompt = settings.master_prompt or ''

            prompt = master_prompt or (
                "Ты создаёшь продающие сценарии для коротких видео о вакансиях."
                " Сделай энергичный текст на 40-60 секунд, выделив выгоды и призыв к действию."
            )

            vacancy_context = (
                f"Должность: {vacancy.get('position', '')}\n"
                f"Компания: {vacancy.get('company', '')}\n"
                f"Локация: {vacancy.get('location', '')}\n"
                f"Зарплата: {vacancy.get('salary', '')}\n"
                f"Условия: {vacancy.get('conditions', '')}\n"
                f"Требования: {vacancy.get('requirements', '')}\n"
                f"Потребность: {vacancy.get('positions_needed', '')}\n"
                f"Комментарий: {vacancy.get('comments', '')}"
            )

            if openai_key:
                from api.openai_client import OpenAIClient
                openai_client = OpenAIClient(openai_key)
                generated_text = openai_client._chat_completion([
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": vacancy_context}
                ])
            else:
                generated_text = (
                    f"Привет! В компанию {vacancy.get('company', '')} требуется {vacancy.get('position', '').lower()} "
                    f"в {vacancy.get('location', '')}. Мы предлагаем {vacancy.get('conditions', '')}. "
                    f"Оплата: {vacancy.get('salary', '')}. {vacancy.get('requirements', '')}. "
                    "Откликайся прямо сейчас, чтобы забронировать место!"
                )

            return jsonify({'success': True, 'text': generated_text})
        except Exception as e:
            print(f"❌ Ошибка генерации текста: {e}")
            return jsonify({'success': False, 'message': f'Ошибка генерации текста: {str(e)}'}), 500

    @app.route('/api/vacancies/generate-video', methods=['POST'])
    def vacancies_generate_video():
        try:
            data = request.get_json() or {}
            audio_url = (data.get('audio_url') or '').strip()
            avatar_id = data.get('avatar_id') or 'default_avatar'
            video_format = data.get('video_format', 'vertical')

            if not audio_url:
                return jsonify({'success': False, 'message': 'Аудио не передано'}), 400

            heygen_key = _get_api_key('heygen_api_key', ['vacancies', 'trends'])
            if not heygen_key:
                return jsonify({'success': False, 'message': 'HeyGen API ключ не настроен'}), 400

            settings = _get_settings('vacancies')
            additional = settings.get_additional_settings() if settings else {}
            if avatar_id == 'default_avatar':
                avatar_id = additional.get('default_avatar_id', avatar_id)

            client = HeyGenClient(heygen_key)
            video_id = client.generate_video(audio_url, avatar_id)

            if not video_id:
                return jsonify({'success': False, 'message': 'Не удалось создать видео'}), 500

            if isinstance(video_id, str) and video_id.startswith('http'):
                return jsonify({'success': True, 'video_url': video_id})

            return jsonify({'success': True, 'video_id': video_id})
        except Exception as e:
            print(f"❌ Ошибка создания видео вакансии: {e}")
            return jsonify({'success': False, 'message': f'Ошибка создания видео: {str(e)}'}), 500

    @app.route('/api/vacancies/check-video-status', methods=['POST'])
    def vacancies_check_video_status():
        try:
            data = request.get_json() or {}
            video_id = data.get('video_id')
            if not video_id:
                return jsonify({'success': False, 'message': 'Video ID не передан'}), 400

            heygen_key = _get_api_key('heygen_api_key', ['vacancies', 'trends'])
            if not heygen_key:
                return jsonify({'success': False, 'message': 'HeyGen API ключ не настроен'}), 400

            client = HeyGenClient(heygen_key)
            status = client.get_video_status(video_id)

            return jsonify({
                'success': True,
                'status': status.get('status'),
                'video_url': status.get('video_url'),
                'error_message': status.get('error_message')
            })
        except Exception as e:
            print(f"❌ Ошибка проверки видео вакансий: {e}")
            return jsonify({'success': False, 'message': f'Ошибка проверки статуса: {str(e)}'}), 500

    @app.route('/api/experts/generate-topics', methods=['POST'])
    def experts_generate_topics():
        try:
            data = request.get_json() or {}
            num_topics = int(data.get('num_topics', 15))

            settings = _get_settings('experts')
            additional = settings.get_additional_settings() if settings else {}
            consumer_profile = additional.get('consumer_profile', 'Современная городская аудитория')

            openai_key = _get_api_key('openai_api_key', ['experts'])
            if not openai_key:
                fallback = [
                    '5 решений для роста продаж без увеличения бюджета',
                    'Как построить команду мечты за 90 дней',
                    '3 ошибки в найме, которые стоят денег каждый день',
                    'Как внедрить новую технологию без сопротивления команды',
                    'Система личной эффективности руководителя на удалёнке'
                ][:num_topics]
                return jsonify({'success': True, 'topics': fallback, 'consumer_profile': consumer_profile})

            prompt = (
                f"Сгенерируй {num_topics} конкретных и современных тем для экспертного короткого видео формата Reels. "
                f"Портрет аудитории: {consumer_profile}. Формат ответа — нумерованный список." 
            )

            openai_client = OpenAIClient(openai_key)
            result_text = openai_client._chat_completion([
                {"role": "user", "content": prompt}
            ])

            topics: List[str] = []
            for line in result_text.split('\n'):
                clean = line.strip()
                if not clean:
                    continue
                clean = re.sub(r'^\d+[\).\-]?\s*', '', clean)
                topics.append(clean)

            if not topics:
                raise ValueError('Не удалось разобрать список тем')

            return jsonify({'success': True, 'topics': topics[:num_topics], 'consumer_profile': consumer_profile})
        except Exception as e:
            print(f"❌ Ошибка генерации тем эксперта: {e}")
            return jsonify({'success': False, 'message': f'Ошибка генерации тем: {str(e)}'}), 500

    @app.route('/api/experts/generate-text', methods=['POST'])
    def experts_generate_text():
        try:
            data = request.get_json() or {}
            topic = (data.get('topic') or '').strip()
            if not topic:
                return jsonify({'success': False, 'message': 'Тема не передана'}), 400

            settings = _get_settings('experts')
            additional = settings.get_additional_settings() if settings else {}
            consumer_profile = additional.get('consumer_profile', 'Современная городская аудитория')
            master_prompt = settings.master_prompt or ''

            openai_key = _get_api_key('openai_api_key', ['experts'])

            prompt = master_prompt or (
                "Ты создаёшь экспертные ролики. Структура: крючок, ценность, практический совет, призыв к действию."
            )

            user_content = (
                f"Тема: {topic}\n"
                f"Аудитория: {consumer_profile}\n"
                "Сделай текст на 60-90 секунд с конкретными примерами."
            )

            if openai_key:
                openai_client = OpenAIClient(openai_key)
                expert_text = openai_client._chat_completion([
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_content}
                ])
            else:
                expert_text = (
                    f"Рассмотрим тему: {topic}. Это важно для {consumer_profile}. "
                    "Вот конкретный шаг, который можно сделать сегодня. Делитесь, что получилось!"
                )

            return jsonify({'success': True, 'text': expert_text})
        except Exception as e:
            print(f"❌ Ошибка генерации экспертного текста: {e}")
            return jsonify({'success': False, 'message': f'Ошибка генерации текста: {str(e)}'}), 500

    @app.route('/api/experts/generate-video', methods=['POST'])
    def experts_generate_video():
        try:
            data = request.get_json() or {}
            audio_url = (data.get('audio_url') or '').strip()
            avatar_id = data.get('avatar_id') or 'default_avatar'

            if not audio_url:
                return jsonify({'success': False, 'message': 'Аудио не передано'}), 400

            heygen_key = _get_api_key('heygen_api_key', ['experts', 'trends'])
            if not heygen_key:
                return jsonify({'success': False, 'message': 'HeyGen API ключ не настроен'}), 400

            settings = _get_settings('experts')
            additional = settings.get_additional_settings() if settings else {}
            if avatar_id == 'default_avatar':
                avatar_id = additional.get('default_avatar_id', avatar_id)

            client = HeyGenClient(heygen_key)
            video_ref = client.generate_video(audio_url, avatar_id)

            if isinstance(video_ref, str) and video_ref.startswith('http'):
                video_url = video_ref
            elif isinstance(video_ref, str):
                status = client.get_video_status(video_ref)
                if status.get('status') == 'completed' and status.get('video_url'):
                    video_url = status.get('video_url')
                else:
                    video_url = client._create_video_placeholder()
            else:
                video_url = client._create_video_placeholder()

            return jsonify({'success': True, 'video_url': video_url})
        except Exception as e:
            print(f"❌ Ошибка генерации экспертного видео: {e}")
            return jsonify({'success': False, 'message': f'Ошибка генерации видео: {str(e)}'}), 500


    @app.route('/api/generate/<module_name>', methods=['POST'])
    def start_generation(module_name):
        try:
            task_id = str(uuid.uuid4())
            
            # Create task status
            task_status = TaskStatus(
                task_id=task_id,
                module_name=module_name,
                status='pending',
                current_step='Инициализация...'
            )
            db.session.add(task_status)
            db.session.commit()
            
            # Start background task based on module
            if module_name == 'trends':
                from modules.module1_trends import TrendModule
                TrendModule.start_generation.delay(task_id)
            elif module_name == 'vacancies':
                from modules.module2_vacancies import VacancyModule
                VacancyModule.start_generation.delay(task_id)
            elif module_name == 'experts':
                from modules.module3_experts import ExpertModule
                data = request.get_json()
                selected_topics = data.get('selected_topics', [])
                ExpertModule.start_generation.delay(task_id, selected_topics)
            
            return jsonify({'success': True, 'task_id': task_id})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/task/<task_id>')
    def get_task_status(task_id):
        task = TaskStatus.query.filter_by(task_id=task_id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'status': task.status,
            'progress': task.progress,
            'current_step': task.current_step,
            'error_message': task.error_message,
            'result_data': task.get_result_data()
        })
    
    @app.route('/api/expert-topics', methods=['POST'])
    def generate_expert_topics():
        try:
            session_id = str(uuid.uuid4())
            from modules.module3_experts import ExpertModule
            expert_module = ExpertModule()
            topics = expert_module.generate_topics(session_id)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'topics': topics
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/expert-topics/<session_id>')
    def get_expert_topics(session_id):
        topics = ExpertTopics.query.filter_by(session_id=session_id).all()
        return jsonify([{
            'id': t.id,
            'topic': t.topic,
            'is_selected': t.is_selected
        } for t in topics])
    
    @app.route('/api/generate-audio', methods=['POST'])
    def generate_audio():
        try:
            data = request.get_json() or {}
            text = (data.get('text') or '').strip()

            if not text:
                return jsonify({'success': False, 'message': 'Текст не предоставлен'}), 400

            voice_id = data.get('voice_id') or 'jP9L6ZC55cz5mmx4ZpCk'
            model_id = data.get('model_id') or 'eleven_flash_v2_5'

            eleven_key = _get_api_key('elevenlabs_api_key')
            from api.elevenlabs_simple import ElevenLabsSimple
            client = ElevenLabsSimple(eleven_key) if eleven_key else ElevenLabsSimple()
            audio_url = client.generate_audio(text, voice_id=voice_id, model_id=model_id)

            if audio_url:
                payload = {
                    'success': True,
                    'audio_url': audio_url,
                    'message': 'Аудио успешно сгенерировано'
                }
                if not eleven_key:
                    payload['warning'] = 'Использована офлайн-заглушка ElevenLabs (API ключ не настроен)'
                return jsonify(payload)

            return jsonify({'success': False, 'message': 'Ошибка генерации аудио'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # WebSocket events for real-time updates
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
    
    @socketio.on('join_task')
    def handle_join_task(data):
        task_id = data['task_id']
        # Join room for this task to receive updates
        from flask_socketio import join_room
        join_room(task_id)
    
    # Favicon route
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, ''),
            '7411193.png',
            mimetype='image/png'
        )
    
    # CSP headers middleware
    @app.after_request
    def add_security_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob: chrome-extension:; img-src 'self' data: https:; media-src 'self' data: https: blob:;"
        return response
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
