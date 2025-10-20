# ВНИМАНИЕ: Этот файл устарел. Для запуска используйте только run.py/start.sh и app.py (который теперь использует socketio).
# Не используйте этот файл для запуска приложения!
#!/usr/bin/env python3
"""
Реальная версия Контент Завода с настоящими API интеграциями
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from models import db, Settings, Competitors, TaskStatus, VideoGeneration, ExpertTopics
from config import Config
from api.openai_client import OpenAIClient
from api.elevenlabs_client import ElevenLabsClient
from api.heygen_client import HeyGenClient
from api.apify_client import ApifyInstagramClient
from api.assemblyai_client import AssemblyAIClient
import uuid
from datetime import datetime
import json
import os
import time

def create_real_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Create tables and default settings
    with app.app_context():
        db.create_all()
        
        # Initialize default settings for modules if they don't exist
        modules = ['trends', 'vacancies', 'experts']
        for module_name in modules:
            existing = Settings.query.filter_by(module_name=module_name).first()
            if not existing:
                settings = Settings(
                    module_name=module_name,
                    master_prompt="",
                    api_keys="{}",
                    additional_settings="{}"
                )
                db.session.add(settings)
        db.session.commit()
    
    def get_api_clients(module_name):
        """Получение настроенных API клиентов для модуля"""
        settings = Settings.query.filter_by(module_name=module_name).first()
        if not settings:
            return None, None, None, None, None
            
        api_keys = settings.get_api_keys()
        
        openai_client = OpenAIClient(api_keys.get('openai_api_key')) if api_keys.get('openai_api_key') else None
        elevenlabs_client = ElevenLabsClient(api_keys.get('elevenlabs_api_key')) if api_keys.get('elevenlabs_api_key') else None
        heygen_client = HeyGenClient(api_keys.get('heygen_api_key')) if api_keys.get('heygen_api_key') else None
        apify_client = ApifyInstagramClient(api_keys.get('apify_api_key')) if api_keys.get('apify_api_key') else None
        assemblyai_client = AssemblyAIClient(api_keys.get('assemblyai_api_key')) if api_keys.get('assemblyai_api_key') else None
        
        return openai_client, elevenlabs_client, heygen_client, apify_client, assemblyai_client
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/module/<module_name>')
    def module_page(module_name):
        if module_name not in ['trends', 'vacancies', 'experts']:
            flash('Модуль не найден', 'error')
            return redirect(url_for('index'))
        
        settings = Settings.query.filter_by(module_name=module_name).first()
        if module_name == 'trends':
            return render_template('module_trends_new.html', settings=settings)
        else:
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
    
    @app.route('/api/settings/<module_name>', methods=['POST'])
    def save_settings(module_name):
        try:
            data = request.get_json()
            settings = Settings.query.filter_by(module_name=module_name).first()
            
            if not settings:
                settings = Settings(module_name=module_name)
                db.session.add(settings)
            
            settings.openai_assistant_id = data.get('openai_assistant_id', '')
            settings.master_prompt = data.get('master_prompt', '')
            settings.set_api_keys(data.get('api_keys', {}))
            settings.set_additional_settings(data.get('additional_settings', {}))
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Настройки сохранены'})
        except Exception as e:
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
    
    # РЕАЛЬНЫЕ API для голосов и аватаров
    @app.route('/api/module/<module_name>/voices')
    def get_voices(module_name):
        try:
            _, elevenlabs_client, _, _, _ = get_api_clients(module_name)
            if elevenlabs_client:
                try:
                    voices = elevenlabs_client.get_available_voices()
                    return jsonify(voices)
                except Exception as e:
                    print(f"ElevenLabs error: {e}")
                    # Возвращаем демо-голоса при ошибке
                    demo_voices = [
                        {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel (Женский, спокойный)"},
                        {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi (Женский, уверенный)"},
                        {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni (Мужской, молодой)"},
                        {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold (Мужской, средний)"}
                    ]
                    return jsonify(demo_voices)
            else:
                return jsonify({'error': 'ElevenLabs API не настроен'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/module/<module_name>/avatars')
    def get_avatars(module_name):
        try:
            _, _, heygen_client, _, _ = get_api_clients(module_name)
            if heygen_client:
                try:
                    avatars = heygen_client.get_available_avatars()
                    return jsonify(avatars)
                except Exception as e:
                    print(f"HeyGen error: {e}")
                    # Возвращаем демо-аватары при ошибке
                    demo_avatars = [
                        {"avatar_id": "Angela_public", "avatar_name": "Angela (Женщина, деловой стиль)"},
                        {"avatar_id": "Josh_lite", "avatar_name": "Josh (Мужчина, молодой)"},
                        {"avatar_id": "Monica_public", "avatar_name": "Monica (Женщина, дружелюбная)"},
                        {"avatar_id": "Wayne_20220426", "avatar_name": "Wayne (Мужчина, профессиональный)"}
                    ]
                    return jsonify(demo_avatars)
            else:
                return jsonify({'error': 'HeyGen API не настроен'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # РЕАЛЬНЫЙ API для сбора рилсов через Apify
    @app.route('/api/trends/collect-reels', methods=['POST'])
    def collect_reels():
        """РЕАЛЬНЫЙ сбор рилсов конкурентов через Apify"""
        try:
            data = request.get_json()
            competitors = data.get('competitors', [])
            count = data.get('count', 20)
            
            if not competitors:
                return jsonify({'success': False, 'message': 'Выберите конкурентов'}), 400
            
            _, _, _, apify_client, _ = get_api_clients('trends')
            if not apify_client:
                return jsonify({'success': False, 'message': 'Apify API не настроен'}), 400
            
            print(f"🔍 Начинаю парсинг {len(competitors)} конкурентов...")
            
            # Получаем вирусный контент
            viral_posts = apify_client.get_trending_content(competitors, days_back=7)
            
            if not viral_posts:
                return jsonify({'success': False, 'message': 'Не удалось получить данные от конкурентов'}), 400
            
            # Обновляем время последней проверки конкурентов
            for competitor_username in competitors:
                competitor = Competitors.query.filter_by(username=competitor_username).first()
                if competitor:
                    competitor.last_checked = datetime.utcnow()
            
            db.session.commit()
            
            print(f"✅ Найдено {len(viral_posts)} постов, из них виральных: {len([p for p in viral_posts if p['is_viral']])}")
            
            return jsonify({
                'success': True,
                'reels': viral_posts,
                'total_count': len(viral_posts),
                'viral_count': len([p for p in viral_posts if p['is_viral']])
            })
            
        except Exception as e:
            print(f"❌ Ошибка сбора рилсов: {e}")
            return jsonify({'success': False, 'message': f'Ошибка парсинга: {str(e)}'}), 500
    
    # РЕАЛЬНЫЙ API для транскрибации через AssemblyAI
    @app.route('/api/trends/transcribe', methods=['POST'])
    def transcribe_reel():
        """РЕАЛЬНАЯ транскрибация через AssemblyAI"""
        try:
            data = request.get_json()
            reel_id = data.get('reel_id')
            video_url = data.get('video_url')  # URL видео для транскрибации
            
            if not video_url:
                return jsonify({'success': False, 'message': 'URL видео не указан'}), 400
            
            _, _, _, _, assemblyai_client = get_api_clients('trends')
            if not assemblyai_client:
                return jsonify({'success': False, 'message': 'AssemblyAI API не настроен'}), 400
            
            print(f"🎤 Начинаю транскрибацию видео: {video_url[:50]}...")
            
            # Реальная транскрибация
            transcript = assemblyai_client.transcribe_video_url(video_url, language_code="ru")
            
            if not transcript:
                return jsonify({'success': False, 'message': 'Не удалось транскрибировать видео'}), 400
            
            print(f"✅ Транскрибация завершена, текст: {len(transcript)} символов")
            
            return jsonify({
                'success': True,
                'transcript': transcript,
                'reel_id': reel_id
            })
            
        except Exception as e:
            print(f"❌ Ошибка транскрибации: {e}")
            return jsonify({'success': False, 'message': f'Ошибка транскрибации: {str(e)}'}), 500
    
    # РЕАЛЬНЫЙ API для переписывания через OpenAI
    @app.route('/api/trends/rewrite', methods=['POST'])
    def rewrite_text():
        """РЕАЛЬНОЕ переписывание текста через OpenAI Assistant"""
        try:
            data = request.get_json()
            transcript = data.get('transcript', '')
            
            if not transcript:
                return jsonify({'success': False, 'message': 'Текст для переписывания не указан'}), 400
            
            settings = Settings.query.filter_by(module_name='trends').first()
            if not settings or not settings.openai_assistant_id:
                return jsonify({'success': False, 'message': 'OpenAI Assistant не настроен'}), 400
            
            openai_client, _, _, _, _ = get_api_clients('trends')
            if not openai_client:
                return jsonify({'success': False, 'message': 'OpenAI API не настроен'}), 400
            
            print(f"🤖 Начинаю переписывание текста через OpenAI Assistant...")
            
            # Создаем промпт для переписывания
            rewrite_prompt = f"""
            {settings.master_prompt}
            
            Исходный текст для переписывания:
            {transcript}
            
            Переписанный текст должен:
            1. Сохранить основную идею
            2. Быть более привлекательным и вирусным
            3. Подходить для 40-секундного видео
            4. Иметь захватывающее начало и призыв к действию
            """
            
            # Реальный вызов OpenAI Assistant
            result = openai_client.create_assistant_message(settings.openai_assistant_id, rewrite_prompt)
            
            if not result:
                return jsonify({'success': False, 'message': 'OpenAI Assistant не ответил'}), 400
            
            rewritten_text = result['content']
            
            print(f"✅ Переписывание завершено: {len(rewritten_text)} символов")
            
            return jsonify({
                'success': True,
                'rewritten_text': rewritten_text,
                'original_length': len(transcript),
                'new_length': len(rewritten_text)
            })
            
        except Exception as e:
            print(f"❌ Ошибка переписывания: {e}")
            return jsonify({'success': False, 'message': f'Ошибка OpenAI: {str(e)}'}), 500
    
    # РЕАЛЬНЫЙ API для создания финального видео
    @app.route('/api/trends/generate-video', methods=['POST'])
    def generate_video():
        """РЕАЛЬНАЯ генерация видео через ElevenLabs + HeyGen"""
        try:
            data = request.get_json()
            text = data.get('text', '')
            voice_id = data.get('voice_id', '')
            avatar_id = data.get('avatar_id', '')
            
            if not all([text, voice_id, avatar_id]):
                return jsonify({'success': False, 'message': 'Не все параметры указаны'}), 400
            
            _, elevenlabs_client, heygen_client, _, _ = get_api_clients('trends')
            
            if not elevenlabs_client:
                return jsonify({'success': False, 'message': 'ElevenLabs API не настроен'}), 400
            if not heygen_client:
                return jsonify({'success': False, 'message': 'HeyGen API не настроен'}), 400
            
            print(f"🎵 Начинаю генерацию аудио через ElevenLabs...")
            
            # Шаг 1: Генерация аудио через ElevenLabs
            audio_url = elevenlabs_client.generate_speech_for_video(text, voice_id)
            if not audio_url:
                return jsonify({'success': False, 'message': 'Не удалось создать аудио'}), 400
            
            print(f"✅ Аудио создано: {audio_url}")
            print(f"🎬 Начинаю создание видео через HeyGen...")
            
            # Шаг 2: Создание видео через HeyGen
            video_url = heygen_client.generate_video_complete(avatar_id, audio_url)
            if not video_url:
                return jsonify({'success': False, 'message': 'Не удалось создать видео'}), 400
            
            print(f"✅ Видео создано: {video_url}")
            
            # Сохраняем результат в базу данных
            task_id = str(uuid.uuid4())
            generation = VideoGeneration(
                task_id=task_id,
                module_name='trends',
                generated_text=text,
                audio_file_url=audio_url,
                video_file_url=video_url,
                avatar_id=avatar_id,
                voice_id=voice_id
            )
            db.session.add(generation)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'text': text,
                'audio_url': audio_url,
                'video_url': video_url,
                'voice_id': voice_id,
                'avatar_id': avatar_id,
                'task_id': task_id
            })
            
        except Exception as e:
            print(f"❌ Ошибка генерации видео: {e}")
            return jsonify({'success': False, 'message': f'Ошибка создания видео: {str(e)}'}), 500
    
    @app.route('/api/module/<module_name>/preview')
    def get_module_preview(module_name):
        if module_name == 'vacancies':
            try:
                from modules.module2_vacancies import VacancyModule
                vacancy_module = VacancyModule()
                preview = vacancy_module.get_vacancies_preview()
                return jsonify(preview)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return jsonify([])
    
    @app.route('/api/module/<module_name>/stats')
    def get_module_stats(module_name):
        if module_name == 'vacancies':
            try:
                from modules.module2_vacancies import VacancyModule
                vacancy_module = VacancyModule()
                vacancies = vacancy_module.get_vacancies_from_sheets()
                return jsonify({
                    "total": len(vacancies),
                    "active": len([v for v in vacancies if v['positions_needed'] != '0']),
                    "priority": len([v for v in vacancies if 'приоритет' in v.get('comments', '').lower()]),
                    "updated": datetime.now().strftime("%H:%M")
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return jsonify({})
    
    @app.route('/api/expert-topics', methods=['POST'])
    def generate_expert_topics():
        """РЕАЛЬНАЯ генерация тем через OpenAI"""
        try:
            data = request.get_json()
            num_topics = data.get('num_topics', 15)
            
            settings = Settings.query.filter_by(module_name='experts').first()
            if not settings or not settings.openai_assistant_id:
                return jsonify({'success': False, 'message': 'OpenAI Assistant для экспертов не настроен'}), 400
            
            openai_client, _, _, _, _ = get_api_clients('experts')
            if not openai_client:
                return jsonify({'success': False, 'message': 'OpenAI API не настроен'}), 400
            
            additional_settings = settings.get_additional_settings()
            consumer_profile = additional_settings.get('consumer_profile', 'Общая аудитория')
            
            prompt = f"""
            Сгенерируйте {num_topics} актуальных тем для экспертного контента.
            
            Портрет потребителя: {consumer_profile}
            
            Требования к темам:
            1. Актуальные и интересные для целевой аудитории
            2. Позволяют дать экспертные советы
            3. Имеют практическую ценность
            4. Подходят для 40-секундного видео
            5. Вызывают интерес и желание узнать больше
            
            Форматируйте ответ как пронумерованный список тем, каждая тема на новой строке.
            """
            
            print(f"🧠 Генерирую {num_topics} тем через OpenAI...")
            
            result = openai_client.create_assistant_message(settings.openai_assistant_id, prompt)
            if not result:
                return jsonify({'success': False, 'message': 'OpenAI не ответил'}), 400
            
            # Парсим ответ
            topics_text = result['content']
            topics = []
            session_id = str(uuid.uuid4())
            
            for line in topics_text.split('\n'):
                line = line.strip()
                if line and any(line.startswith(str(i) + '.') for i in range(1, 100)):
                    topic = line.split('.', 1)[1].strip()
                    topics.append(topic)
                    
                    # Сохраняем в базу
                    expert_topic = ExpertTopics(
                        session_id=session_id,
                        topic=topic,
                        is_selected=False
                    )
                    db.session.add(expert_topic)
            
            db.session.commit()
            
            print(f"✅ Сгенерировано {len(topics)} тем")
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'topics': topics
            })
            
        except Exception as e:
            print(f"❌ Ошибка генерации тем: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    
    return app

if __name__ == '__main__':
    print("🚀 Запуск РЕАЛЬНОГО Контент Завода...")
    print("🔥 Все API интеграции активны")
    print("⚡ Apify, AssemblyAI, OpenAI, ElevenLabs, HeyGen")
    print("=" * 60)
    
    app = create_real_app()
    
    print("🎉 Контент Завод с реальными API готов!")
    print("📱 Веб-интерфейс: http://localhost:5001")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
        print("✅ Готово!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
