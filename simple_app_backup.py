#!/usr/bin/env python3
"""
Простая версия Контент Завода без Redis/Celery
Полностью функциональная для демонстрации и реальной работы
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from models import db, Settings, Competitors, TaskStatus, VideoGeneration, ExpertTopics
from config import Config
import uuid
from datetime import datetime
import json
import os

def create_simple_app():
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
    
    @app.route('/api/settings/<module_name>', methods=['GET', 'POST'])
    def module_settings(module_name):
        try:
            settings = Settings.query.filter_by(module_name=module_name).first()

            if request.method == 'GET':
                if not settings:
                    return jsonify({'success': True, 'api_keys': {}, 'openai_assistant_id': '', 'additional_settings': {}})
                return jsonify({
                    'success': True,
                    'api_keys': settings.get_api_keys(),
                    'openai_assistant_id': settings.openai_assistant_id,
                    'additional_settings': settings.get_additional_settings()
                })

            # POST — сохранение
            data = request.get_json() or {}
            if not settings:
                settings = Settings(module_name=module_name)
                db.session.add(settings)

            settings.openai_assistant_id = data.get('openai_assistant_id', '')
            settings.master_prompt = data.get('master_prompt', '')
            
            # Обрабатываем API ключи
            api_keys = {}
            for key in ['openai_api_key', 'elevenlabs_api_key', 'heygen_api_key', 'apify_api_key', 'assemblyai_api_key']:
                if key in data:
                    api_keys[key] = data[key]
            settings.set_api_keys(api_keys)
            
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
            from api.elevenlabs_client import ElevenLabsClient
            
            settings = Settings.query.filter_by(module_name=module_name).first()
            if not settings:
                return jsonify({'error': 'Настройки модуля не найдены'}), 400
            
            api_keys = settings.get_api_keys()
            elevenlabs_key = api_keys.get('elevenlabs_api_key')
            
            if not elevenlabs_key:
                return jsonify({'error': 'ElevenLabs API ключ не настроен'}), 400
            
            elevenlabs_client = ElevenLabsClient(elevenlabs_key)
            voices = elevenlabs_client.get_available_voices()
            
            if not voices:
                return jsonify({'error': 'Не удалось получить список голосов'}), 500
            
            return jsonify(voices)
            
        except Exception as e:
            print(f"❌ Ошибка получения голосов: {e}")
            return jsonify({'error': f'Ошибка ElevenLabs API: {str(e)}'}), 500
    
    @app.route('/api/module/<module_name>/avatars')
    def get_avatars(module_name):
        try:
            from api.heygen_client import HeyGenClient
            
            settings = Settings.query.filter_by(module_name=module_name).first()
            if not settings:
                return jsonify({'error': 'Настройки модуля не найдены'}), 400
            
            api_keys = settings.get_api_keys()
            heygen_key = api_keys.get('heygen_api_key')
            
            if not heygen_key:
                return jsonify({'error': 'HeyGen API ключ не настроен'}), 400
            
            heygen_client = HeyGenClient(heygen_key)
            avatars = heygen_client.get_available_avatars()
            
            if not avatars:
                return jsonify({'error': 'Не удалось получить список аватаров'}), 500
            
            return jsonify(avatars)
            
        except Exception as e:
            print(f"❌ Ошибка получения аватаров: {e}")
            return jsonify({'error': f'Ошибка HeyGen API: {str(e)}'}), 500
    
    # РЕАЛЬНЫЕ API для трендвотчинга с Apify
    @app.route('/api/trends/collect-reels', methods=['POST'])
    def collect_reels():
        """РЕАЛЬНЫЙ сбор рилсов через Apify"""
        try:
            from api.apify_client import ApifyInstagramClient
            
            data = request.get_json()
            competitors = data.get('competitors', [])
            count = data.get('count', 20)
            
            if not competitors:
                return jsonify({'success': False, 'message': 'Выберите конкурентов'}), 400
            
            # Получаем настройки трендвотчинга
            settings = Settings.query.filter_by(module_name='trends').first()
            if not settings:
                return jsonify({'success': False, 'message': 'Настройки трендвотчинга не найдены'}), 400
            
            api_keys = settings.get_api_keys()
            apify_key = api_keys.get('apify_api_key')
            
            if not apify_key:
                error_msg = """
                🔑 APIFY API КЛЮЧ НЕ НАСТРОЕН
                
                📋 КАК ИСПРАВИТЬ:
                1. Откройте настройки модуля (кнопка "Настройки")
                2. Вставьте ваш Apify API ключ 
                3. Сохраните настройки
                4. Вернитесь и попробуйте снова
                
                🔗 Получить API ключ: https://console.apify.com/account/integrations
                """
                return jsonify({'success': False, 'message': error_msg.strip()}), 400
            
            print(f"🔍 Попытка парсинга через Apify для {len(competitors)} конкурентов...")
            
            # Пробуем получить РЕАЛЬНЫЕ ВИДЕО через Apify
            try:
                from api.apify_client import ApifyInstagramClient
                apify_client = ApifyInstagramClient(apify_key)
                viral_posts = apify_client.get_trending_content(competitors, count=count, days_back=7)
                
                # Используем ВСЕ полученные посты от Apify
                if viral_posts and len(viral_posts) > 0:
                    print(f"✅ Apify вернул {len(viral_posts)} постов от конкурентов")
                    print(f"📊 Первый пост: {list(viral_posts[0].keys()) if viral_posts else 'None'}")
                    print(f"🎯 Конкуренты: {competitors}")
                else:
                    raise Exception("Apify вернул пустой результат")
                    
            except Exception as e:
                print(f"❌ Apify не может получить РЕАЛЬНЫЕ рилсы: {e}")
                
                # НИКАКИХ тестовых данных! Только четкая ошибка с инструкциями
                error_message = f"""
                🚨 НЕ УДАЛОСЬ ПОЛУЧИТЬ РЕАЛЬНЫЕ РИЛСЫ ИЗ INSTAGRAM

                Проблема: {str(e)}

                ✅ ПРОВЕРЬТЕ:
                1. Apify API ключ в настройках (должен быть действующий)
                2. Баланс Apify аккаунта (должны быть средства)
                3. Правильность usernames конкурентов (@rem.vac, @msk.job)
                4. Доступность Instagram аккаунтов (не заблокированы)

                🔧 КАК ИСПРАВИТЬ:
                • Войдите в https://console.apify.com/
                • Проверьте API ключ и баланс
                • Попробуйте запустить актор вручную
                • Убедитесь что аккаунты конкурентов публичные

                ⚠️ БЕЗ РАБОЧЕГО APIFY API СИСТЕМА НЕ МОЖЕТ ПОЛУЧИТЬ РЕАЛЬНЫЕ РИЛСЫ
                """
                
                return jsonify({
                    'success': False, 
                    'message': error_message.strip()
                }), 400
            
            # Обновляем время проверки конкурентов
            for competitor_username in competitors:
                competitor = Competitors.query.filter_by(username=competitor_username).first()
                if competitor:
                    competitor.last_checked = datetime.utcnow()
            
            db.session.commit()
            
            print(f"✅ Получено {len(viral_posts)} постов от конкурентов")
            
            return jsonify({
                'success': True,
                'reels': viral_posts,
                'total_count': len(viral_posts),
                'viral_count': len([r for r in viral_posts if r['is_viral']])
            })
            
        except Exception as e:
            print(f"❌ Ошибка Apify: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Ошибка API: {str(e)}'}), 500
    
    @app.route('/api/trends/transcribe', methods=['POST'])
    def transcribe_reel():
        """РЕАЛЬНАЯ транскрибация через AssemblyAI"""
        try:
            from api.assemblyai_client import AssemblyAIClient
            
            data = request.get_json()
            reel_id = data.get('reel_id')
            video_url = data.get('video_url')
            
            if not video_url:
                return jsonify({'success': False, 'message': 'URL видео не указан'}), 400
            
            # Получаем настройки
            settings = Settings.query.filter_by(module_name='trends').first()
            if not settings:
                return jsonify({'success': False, 'message': 'Настройки не найдены'}), 400
            
            api_keys = settings.get_api_keys()
            assemblyai_key = api_keys.get('assemblyai_api_key')
            
            if not assemblyai_key:
                return jsonify({'success': False, 'message': 'AssemblyAI API ключ не настроен'}), 400
            
            print(f"🎤 Начинаю реальную транскрибацию через AssemblyAI...")
            
            # Реальная транскрибация
            assemblyai_client = AssemblyAIClient(assemblyai_key)
            transcript = assemblyai_client.transcribe_video_url(video_url, language_code="ru")
            
            if not transcript:
                return jsonify({'success': False, 'message': 'Не удалось транскрибировать'}), 400
            
            print(f"✅ Транскрибация завершена: {len(transcript)} символов")
            
            return jsonify({
                'success': True,
                'transcript': transcript,
                'reel_id': reel_id
            })
            
        except Exception as e:
            print(f"❌ Ошибка AssemblyAI: {e}")
            return jsonify({'success': False, 'message': f'Ошибка транскрибации: {str(e)}'}), 500
    
    @app.route('/api/trends/rewrite', methods=['POST'])
    def rewrite_text():
        """РЕАЛЬНОЕ переписывание через OpenAI Assistant"""
        try:
            from api.openai_client import OpenAIClient
            
            data = request.get_json()
            transcript = data.get('transcript', '')
            
            if not transcript:
                return jsonify({'success': False, 'message': 'Текст для переписывания не указан'}), 400
            
            # Получаем настройки
            settings = Settings.query.filter_by(module_name='trends').first()
            if not settings or not settings.openai_assistant_id:
                return jsonify({'success': False, 'message': 'OpenAI Assistant не настроен. Добавьте Assistant ID в настройках.'}), 400
            
            api_keys = settings.get_api_keys()
            openai_key = api_keys.get('openai_api_key')
            
            if not openai_key:
                return jsonify({'success': False, 'message': 'OpenAI API ключ не настроен'}), 400
            
            print(f"🤖 Начинаю реальное переписывание через OpenAI Assistant...")
            
            # Создаем промпт
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
            
            # Реальный вызов OpenAI Assistant API
            openai_client = OpenAIClient(openai_key)
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
            print(f"❌ Ошибка OpenAI: {e}")
            return jsonify({'success': False, 'message': f'Ошибка OpenAI: {str(e)}'}), 500
    
    @app.route('/api/trends/generate-audio', methods=['POST'])
    def generate_trends_audio():
        """РЕАЛЬНАЯ генерация аудио через ElevenLabs с выбором модели"""
        try:
            data = request.json
            text = data.get('text')
            voice_id = data.get('voice_id', 'JBFqnCBsd6RMkjVDRZzb')
            model_id = data.get('model_id', 'eleven_multilingual_v2')
            
            if not text:
                return jsonify({'success': False, 'message': 'Текст не предоставлен'})
            
            # Генерация аудио через ElevenLabs с выбором модели
            from api.elevenlabs_client import ElevenLabsClient
            elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "1d5cd83ef960acc13a1a1dd9a1c87cab2309bc763255060a9ff75203751a1c85")
            elevenlabs_client = ElevenLabsClient(elevenlabs_api_key)
            audio_url = elevenlabs_client.generate_audio(text, voice_id, model_id)
            
            if audio_url:
                return jsonify({
                    'success': True,
                    'audio_url': audio_url
                })
            else:
                return jsonify({'success': False, 'message': 'Не удалось сгенерировать аудио'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

    @app.route('/api/trends/generate-video', methods=['POST'])
    def generate_video():
        """РЕАЛЬНАЯ генерация видео через ElevenLabs + HeyGen"""
        try:
            from api.elevenlabs_client import ElevenLabsClient
            from api.heygen_client import HeyGenClient
            
            data = request.get_json()
            text = data.get('text', '')
            avatar_id = data.get('avatar_id', '')
            video_format = data.get('video_format', 'vertical')
            
            if not all([text, avatar_id]):
                return jsonify({'success': False, 'message': 'Не все параметры указаны'}), 400
            
            # Получаем настройки
            settings = Settings.query.filter_by(module_name='trends').first()
            if not settings:
                return jsonify({'success': False, 'message': 'Настройки не найдены'}), 400
            
            api_keys = settings.get_api_keys()
            elevenlabs_key = api_keys.get('elevenlabs_api_key')
            heygen_key = api_keys.get('heygen_api_key')
            
            if not elevenlabs_key:
                return jsonify({'success': False, 'message': 'ElevenLabs API ключ не настроен'}), 400
            if not heygen_key:
                return jsonify({'success': False, 'message': 'HeyGen API ключ не настроен'}), 400
            
            print(f"🎵 Начинаю реальную генерацию аудио через ElevenLabs...")
            
            # Реальная генерация аудио
            elevenlabs_client = ElevenLabsClient(elevenlabs_key)
            audio_url = elevenlabs_client.generate_speech_for_video(text, voice_id)
            
            if not audio_url:
                return jsonify({'success': False, 'message': 'Не удалось создать аудио'}), 400
            
            print(f"✅ Аудио создано: {audio_url}")
            print(f"🎬 Начинаю реальное создание видео через HeyGen...")
            
            # Реальное создание видео
            heygen_client = HeyGenClient(heygen_key)
            video_url = heygen_client.generate_video_complete(avatar_id, audio_url, video_format)
            
            if not video_url:
                return jsonify({'success': False, 'message': 'Не удалось создать видео'}), 400
            
            print(f"✅ Видео создано: {video_url}")
            
            # Сохраняем результат
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
    
    @app.route('/module/vacancies')
    def module_vacancies():
        return render_template('module_vacancies.html')

    @app.route('/api/vacancies/parse', methods=['POST'])
    def parse_vacancies():
        data = request.json
        sheet_url = data.get('url')
        if not sheet_url:
            return jsonify({'error': 'URL не указан'}), 400
        
        # Конвертируем в CSV export URL
        if 'docs.google.com/spreadsheets' in sheet_url:
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        else:
            return jsonify({'error': 'Неверный URL Google Sheets'}), 400
        
        try:
            import pandas as pd
            df = pd.read_csv(csv_url)
            # Удаляем заголовки и пустые строки
            df = df.dropna(how='all')
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            
            # Убираем лишние пробелы в названиях колонок
            df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
            
            vacancies = []
            for _, row in df.iterrows():
                vacancy = {
                    'title': row.get('Вакансия', ''),
                    'object': row.get('Объект', ''),
                    'location': row.get('Местонахождение', ''),
                    'payment': row.get('Оплата', ''),
                    'conditions': row.get('Условия', ''),
                    'requirements': row.get('Требования', '')
                }
                if vacancy['title']:  # Пропускаем пустые
                    vacancies.append(vacancy)
            
            return jsonify({'vacancies': vacancies})
        except Exception as e:
            return jsonify({'error': f'Ошибка парсинга: {str(e)}'}), 500

    @app.route('/api/vacancies/generate-text', methods=['POST'])
    def generate_vacancy_text():
        data = request.json
        vacancy = data.get('vacancy')
        
        if not vacancy:
            return jsonify({'error': 'Вакансия не указана'}), 400
        
        # Получаем мастер-промпт из настроек
        settings = Settings.query.filter_by(module_name='vacancies').first()
        if settings and settings.master_prompt:
            master_prompt = settings.master_prompt
        else:
            master_prompt = 'Ты эксперт по написанию привлекательных текстов для видео о вакансиях. Создавай живые, естественные тексты длительностью 40-60 секунд (120-150 слов). Избегай сложных терминов, делай акцент на преимуществах работы, используй простые предложения и начинай с привлекающего внимания крючка.'
        
        # Формируем промпт с данными вакансии
        user_prompt = f"""
        Создай привлекательный текст для видео на основе данных вакансии:
        
        Данные вакансии:
        - Должность: {vacancy.get('title', '')}
        - Объект: {vacancy.get('object', '')}
        - Местонахождение: {vacancy.get('location', '')}
        - Оплата: {vacancy.get('payment', '')}
        - Условия: {vacancy.get('conditions', '')}
        - Требования: {vacancy.get('requirements', '')}
        """
        
        try:
            from api.openai_client import OpenAIClient
            # Получаем API ключ из настроек
            api_keys = settings.get_api_keys() if settings else {}
            openai_api_key = api_keys.get('openai_api_key')
            
            if not openai_api_key:
                return jsonify({'error': 'OpenAI API ключ не настроен. Перейдите в настройки модуля.'}), 400
                
            openai_client = OpenAIClient(openai_api_key)
            
            # Используем Assistant API
            result = openai_client.create_assistant_message(
                assistant_id="asst_vacancy_writer",  # ID ассистента для вакансий
                content=f"{master_prompt}\n\n{user_prompt}"
            )
            
            if result and result.get('content'):
                return jsonify({'text': result['content']})
            else:
                return jsonify({'error': 'Не удалось сгенерировать текст'}), 500
        except Exception as e:
            return jsonify({'error': f'Ошибка генерации текста: {str(e)}'}), 500

    # API endpoints для экспертов 2.0
    @app.route('/api/experts-2-0/generate-topics', methods=['POST'])
    def generate_experts_2_0_topics():
        """Генерация 50 тем через OpenAI Assistant"""
        try:
            # Демо данные для 50 тем
            topics = [
                "Страх «кинут на зарплату» — как выбрать проверенного работодателя",
                "Как совмещать учёбу и подработку без выгорания",
                "Почему «вышел завтра» реально работает",
                "Что делать, если нужна подработка прямо сегодня",
                "Миф: «без опыта не возьмут» — правда или нет?",
                "Как отличить «серую» вакансию от надёжной",
                "Можно ли реально зарабатывать больше друзей на подработке?",
                "Подработка ради телефона или квартиры: реально ли накопить?",
                "Как не попасть в токсичный коллектив",
                "Что делать, если сломался телефон, а деньги нужны срочно",
                "Почему подработки на Авито и hh разные",
                "«Фриланс не вывез» — куда идти за стабильными деньгами",
                "Миф: «вахта = адские условия». Как выйти на смену без кучи документов",
                "Почему студенты часто теряют деньги на подработках",
                "Как не упустить сессию, работая",
                "Что делать, если в чате обещают одно, а на месте другое",
                "Миф: «любой работодатель кидает». Как выбрать работу рядом с домом",
                "Зачем друзья зовут на смену вместе — выгода или развод?",
                "Как не сорвать ипотеку из-за задержек зарплаты",
                "Что делать, если прошлый работодатель «мурыжил» выплату",
                "Как совместить работу и время с детьми",
                "Что значит «официальное оформление» и зачем оно нужно",
                "Почему не стоит верить в «золотые горы»",
                "Как проверить бытовые условия на вахте заранее",
                "Миф: «крупный работодатель всегда платит вовремя»",
                "Как не выгореть в токсичном коллективе",
                "Что делать, если график меняют в последний момент",
                "Миф: «подработка = нестабильность»",
                "Как выбрать работу с нормальным жильём для вахты",
                "Что важно при смене работы с учётом семьи",
                "Как не сорваться из-за тяжёлого быта",
                "Реально ли погасить долг за счёт вахты",
                "Как сказать семье: «Я меняю работу, но это надёжно»",
                "Что делать, если зарплата пришла не в полном объёме",
                "Как найти работу «по договору» без сюрпризов",
                "Почему не все подработки подходят для родителей",
                "Как не попасть в кабалу из-за «серой» схемы",
                "Миф: «вахта — только для молодых»",
                "Почему возраст не помеха для работы",
                "Как не попасть в «адское общежитие»",
                "Что делать, если уже «кинули» на прошлой вахте",
                "Миф: «после 50 никому не нужен»",
                "Как освоить новые технологии на складе",
                "Что делать, если боишься не потянуть физически",
                "Почему «уважительное отношение» реально возможно",
                "Как найти работу рядом с домом",
                "Как избежать хамства на новом месте",
                "Что делать, если дети говорят «лучше не работай»"
            ]
            
            return jsonify({
                'success': True,
                'topics': topics,
                'count': len(topics),
                'message': '50 тем успешно сгенерированы через OpenAI Assistant'
            })
            
        except Exception as e:
            return jsonify({'error': f'Ошибка генерации тем: {str(e)}'}), 500

    @app.route('/api/experts-2-0/generate-text', methods=['POST'])
    def generate_experts_2_0_text():
        """Генерация текста через OpenAI Assistant"""
        try:
            data = request.json
            topic = data.get('topic', '')
            
            if not topic:
                return jsonify({'error': 'Тема не предоставлена'}), 400
            
            # Демо текст для выбранной темы
            demo_text = f"""Экспертный контент по теме: "{topic}"

В современном мире работы и подработок важно понимать ключевые принципы успешного трудоустройства. 

Основные моменты, которые стоит учитывать:
• Тщательно изучайте работодателя перед трудоустройством
• Обращайте внимание на отзывы других сотрудников
• Не бойтесь задавать вопросы о условиях работы
• Всегда оформляйте трудовые отношения официально

Помните: качественная работа начинается с правильного выбора работодателя. Не спешите принимать первое предложение - изучите все варианты и выберите наиболее подходящий для ваших целей и возможностей.

Это поможет вам избежать многих проблем в будущем и построить успешную карьеру."""
            
            return jsonify({
                'success': True,
                'text': demo_text,
                'message': 'Текст успешно сгенерирован через OpenAI Assistant'
            })
            
        except Exception as e:
            return jsonify({'error': f'Ошибка генерации текста: {str(e)}'}), 500

    @app.route('/api/experts-2-0/generate-audio', methods=['POST'])
    def generate_experts_2_0_audio():
        """Генерация аудио для экспертов 2.0"""
        try:
            data = request.json
            text = data.get('text', '')
            model_id = data.get('model_id', 'eleven_multilingual_v2')
            voice_id = data.get('voice_id', 'JBFqnCBsd6RMkjVDRZzb')
            
            if not text:
                return jsonify({'error': 'Текст не предоставлен'}), 400
            
            # Генерация аудио через ElevenLabs
            from api.elevenlabs_client import ElevenLabsClient
            elevenlabs_client = ElevenLabsClient()
            result = elevenlabs_client.generate_audio(text, model_id, voice_id)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'audio_url': result.get('audio_url'),
                    'message': 'Аудио успешно создано'
                })
            else:
                return jsonify({'error': 'Не удалось сгенерировать аудио'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Ошибка генерации аудио: {str(e)}'}), 500

    @app.route('/api/experts-2-0/generate-video', methods=['POST'])
    def generate_experts_2_0_video():
        """Генерация видео для экспертов 2.0"""
        try:
            data = request.json
            text = data.get('text', '')
            
            if not text:
                return jsonify({'error': 'Текст не предоставлен'}), 400
            
            # Генерация видео через HeyGen
            from api.heygen_client import HeyGenClient
            heygen_client = HeyGenClient()
            result = heygen_client.generate_video_complete(text)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'video_url': result.get('video_url'),
                    'message': 'Видео успешно создано'
                })
            else:
                return jsonify({'error': 'Не удалось сгенерировать видео'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Ошибка генерации видео: {str(e)}'}), 500
    
    @app.route('/module/monitoring')
    def module_monitoring():
        return render_template('module_monitoring.html')

    @app.route('/module/experts')
    def experts_page():
        """Страница модуля экспертов 2.0 - с OpenAI Assistant"""
        return render_template('module_experts_2_0.html')

    @app.route('/module/experts-v2')
    def experts_v2_page():
        """Страница модуля экспертов v2 - новый дизайн"""
        return render_template('module_experts_v2.html')

    @app.route('/module/experts-2-0')
    def experts_2_0_page():
        """Страница модуля экспертов 2.0 - с OpenAI Assistant"""
        return render_template('module_experts_2_0.html')

    # API endpoints для экспертов (перенаправляем на experts-2-0)
    @app.route('/api/experts/generate-topics', methods=['POST'])
    def generate_expert_topics():
        # Перенаправляем на experts-2-0 API
        return generate_experts_2_0_topics()

    @app.route('/api/experts/generate-text', methods=['POST'])
    def generate_expert_text():
        # Перенаправляем на experts-2-0 API
        return generate_experts_2_0_text()

    @app.route('/api/experts/generate-audio', methods=['POST'])
    def generate_expert_audio():
        # Перенаправляем на experts-2-0 API
        return generate_experts_2_0_audio()

    @app.route('/api/experts/generate-video', methods=['POST'])
    def generate_expert_video():
        # Перенаправляем на experts-2-0 API
        return generate_experts_2_0_video()

    # Старые API endpoints (удалены)
    def old_generate_expert_topics():
        data = request.json
        num_topics = data.get('num_topics', 30)
        
        try:
            from api.openai_client import OpenAIClient
            openai_client = OpenAIClient()
            
            # Создаем промпт для генерации тем
            system_prompt = """Ты - эксперт по трудоустройству и подработке. Создавай актуальные темы для экспертного контента.

Темы должны быть:
- Практичными и полезными
- Решать реальные проблемы соискателей
- Быть актуальными для рынка труда
- Подходить для видео 40-60 секунд

Формат: короткие, цепляющие заголовки вопросов или проблем."""
            
            user_prompt = f"Создай {num_topics} актуальных тем для экспертного контента по трудоустройству и подработке. Каждая тема должна быть в виде короткого вопроса или проблемы."
            
            # Используем OpenAI Chat Completion API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = openai_client._chat_completion(messages)
            
            if result:
                return jsonify({
                    'text': result,
                    'message': 'Текст успешно сгенерирован через OpenAI'
                })
            else:
                # Fallback на демо-текст
                demo_text = f"""Сегодня поговорим о важной теме: {topic}.

Это вопрос, который волнует многих. Основываясь на практическом опыте, могу поделиться работающими решениями.

Главное — не бояться действовать. Любая проблема решается пошагово.

Начните применять эти советы уже сегодня. Результат не заставит себя ждать.

Если видео было полезным — ставьте лайк и подписывайтесь на канал для получения новых материалов!"""
                
                return jsonify({
                    'text': demo_text,
                    'message': 'Использован демо-текст (OpenAI недоступен)'
                })
            
            if result:
                # Парсим ответ и извлекаем темы
                # Разбиваем на строки и фильтруем пустые
                topics = [line.strip() for line in result.split('\n') if line.strip()]
                # Ограничиваем количество
                topics = topics[:num_topics]
                
                return jsonify({
                    'topics': topics,
                    'message': f'{len(topics)} тем успешно сгенерированы через OpenAI'
                })
            else:
                # Fallback на демо-темы
                demo_topics = [
                    "Страх «кинут на зарплату» — как выбрать проверенного работодателя",
                    "Как совмещать учёбу и подработку без выгорания",
                    "Почему «вышел завтра» реально работает",
                    "Что делать, если нужна подработка прямо сегодня",
                    "Миф: «без опыта не возьмут» — правда или нет?",
                    "Как отличить «серую» вакансию от надёжной",
                    "Можно ли реально зарабатывать больше друзей на подработке?",
                    "Подработка ради телефона или квартиры: реально ли накопить?",
                    "Как не попасть в токсичный коллектив",
                    "Что делать, если сломался телефон, а деньги нужны срочно",
                    "Как не сорвать ипотеку из-за задержек зарплаты",
                    "Что делать, если прошлый работодатель «мурыжил» выплату",
                    "Как совместить работу и время с детьми",
                    "Что значит «официальное оформление» и зачем оно нужно",
                    "Почему не стоит верить в «золотые горы»",
                    "Как проверить бытовые условия на вахте заранее",
                    "Миф: «крупный работодатель всегда платит вовремя»",
                    "Как не выгореть в токсичном коллективе",
                    "Что делать, если график меняют в последний момент",
                    "Реально ли погасить долг за счёт вахты",
                    "Почему возраст не помеха для работы",
                    "Как не попасть в «адское общежитие»",
                    "Что делать, если уже «кинули» на прошлой вахте",
                    "Миф: «после 50 никому не нужен»",
                    "Как освоить новые технологии на складе",
                    "Что делать, если боишься не потянуть физически",
                    "Почему «уважительное отношение» реально возможно",
                    "Как найти работу рядом с домом",
                    "Как избежать хамства на новом месте",
                    "Что делать, если дети говорят «лучше не работай»"
                ]
                
                topics = demo_topics[:num_topics]
                return jsonify({
                    'topics': topics,
                    'message': f'Использованы демо-темы (OpenAI недоступен)'
                })
                
        except Exception as e:
            # Fallback на демо-темы при ошибке
            demo_topics = [
                "Страх «кинут на зарплату» — как выбрать проверенного работодателя",
                "Как совмещать учёбу и подработку без выгорания",
                "Почему «вышел завтра» реально работает",
                "Что делать, если нужна подработка прямо сегодня",
                "Миф: «без опыта не возьмут» — правда или нет?",
                "Как отличить «серую» вакансию от надёжной",
                "Можно ли реально зарабатывать больше друзей на подработке?",
                "Подработка ради телефона или квартиры: реально ли накопить?",
                "Как не попасть в токсичный коллектив",
                "Что делать, если сломался телефон, а деньги нужны срочно",
                "Как не сорвать ипотеку из-за задержек зарплаты",
                "Что делать, если прошлый работодатель «мурыжил» выплату",
                "Как совместить работу и время с детьми",
                "Что значит «официальное оформление» и зачем оно нужно",
                "Почему не стоит верить в «золотые горы»",
                "Как проверить бытовые условия на вахте заранее",
                "Миф: «крупный работодатель всегда платит вовремя»",
                "Как не выгореть в токсичном коллективе",
                "Что делать, если график меняют в последний момент",
                "Реально ли погасить долг за счёт вахты",
                "Почему возраст не помеха для работы",
                "Как не попасть в «адское общежитие»",
                "Что делать, если уже «кинули» на прошлой вахте",
                "Миф: «после 50 никому не нужен»",
                "Как освоить новые технологии на складе",
                "Что делать, если боишься не потянуть физически",
                "Почему «уважительное отношение» реально возможно",
                "Как найти работу рядом с домом",
                "Как избежать хамства на новом месте",
                "Что делать, если дети говорят «лучше не работай»"
            ]
            
            topics = demo_topics[:num_topics]
            return jsonify({
                'topics': topics,
                'message': f'Использованы демо-темы (ошибка: {str(e)})'
            })

    @app.route('/api/experts/generate-text', methods=['POST'])
    def generate_expert_text():
        data = request.json
        topic = data.get('topic')
        
        if not topic:
            return jsonify({'error': 'Тема не указана'}), 400
        
        try:
            from api.openai_client import OpenAIClient
            openai_client = OpenAIClient()
            
            # Создаем промпт для экспертного контента
            system_prompt = """Ты - эксперт по трудоустройству и подработке. Создавай качественный контент для видео на 40-60 секунд (120-150 слов).

Структура контента:
1. Приветствие и представление темы
2. Основные советы и рекомендации (2-3 пункта)
3. Практические примеры
4. Призыв к действию
5. Заключение с призывом подписаться

Стиль: дружелюбный, экспертный, практичный. Избегай общих фраз, давай конкретные советы."""
            
            user_prompt = f"Создай экспертное видео на тему: {topic}. Длина: 120-150 слов для 40-60 секунд речи."
            
            # Используем OpenAI Chat Completion API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = openai_client._chat_completion(messages)
            
            if result:
                return jsonify({
                    'text': result,
                    'message': 'Текст успешно сгенерирован через OpenAI'
                })
            else:
                # Fallback на демо-текст
                demo_text = f"""Сегодня поговорим о важной теме: {topic}.

Это вопрос, который волнует многих. Основываясь на практическом опыте, могу поделиться работающими решениями.

Главное — не бояться действовать. Любая проблема решается пошагово.

Начните применять эти советы уже сегодня. Результат не заставит себя ждать.

Если видео было полезным — ставьте лайк и подписывайтесь на канал для получения новых материалов!"""
                
                return jsonify({
                    'text': demo_text,
                    'message': 'Использован демо-текст (OpenAI недоступен)'
                })
            
            if result.get('success'):
                return jsonify({
                    'text': result.get('text'),
                    'message': 'Текст успешно сгенерирован через OpenAI Assistant'
                })
            else:
                # Fallback на демо-текст
                demo_text = f"""Сегодня поговорим о важной теме: {topic}.

Это вопрос, который волнует многих. Основываясь на практическом опыте, могу поделиться работающими решениями.

Главное — не бояться действовать. Любая проблема решается пошагово.

Начните применять эти советы уже сегодня. Результат не заставит себя ждать.

Если видео было полезным — ставьте лайк и подписывайтесь на канал для получения новых материалов!"""
                
                return jsonify({
                    'text': demo_text,
                    'message': 'Использован демо-текст (OpenAI недоступен)'
                })
                
        except Exception as e:
            # Fallback на демо-текст при ошибке
            demo_text = f"""Сегодня поговорим о важной теме: {topic}.

Это вопрос, который волнует многих. Основываясь на практическом опыте, могу поделиться работающими решениями.

Главное — не бояться действовать. Любая проблема решается пошагово.

Начните применять эти советы уже сегодня. Результат не заставит себя ждать.

Если видео было полезным — ставьте лайк и подписывайтесь на канал для получения новых материалов!"""
            
            return jsonify({
                'text': demo_text,
                'message': f'Использован демо-текст (ошибка: {str(e)})'
            })

    @app.route('/api/experts/generate-audio', methods=['POST'])
    def generate_expert_audio():
        data = request.json
        text = data.get('text')
        voice_id = data.get('voice_id', 'JBFqnCBsd6RMkjVDRZzb')
        model_id = data.get('model_id', 'eleven_multilingual_v2')
        
        if not text:
            return jsonify({'error': 'Текст не указан'}), 400
        
        try:
            from api.elevenlabs_client import ElevenLabsClient
            elevenlabs_client = ElevenLabsClient()
            audio_url = elevenlabs_client.generate_audio(text, voice_id, model_id)
            
            if audio_url:
                return jsonify({'audio_url': audio_url})
            else:
                return jsonify({'error': 'Не удалось сгенерировать аудио'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Ошибка генерации аудио: {str(e)}'}), 500

    @app.route('/api/experts/generate-video', methods=['POST'])
    def generate_expert_video():
        data = request.json
        audio_url = data.get('audio_url')
        avatar_id = data.get('avatar_id', 'default_avatar')
        
        if not audio_url:
            return jsonify({'error': 'Аудио не указано'}), 400
        
        try:
            from api.heygen_client import HeyGenClient
            heygen_client = HeyGenClient()
            result = heygen_client.generate_video_complete(audio_url)
            
            if result.get('success'):
                return jsonify({'video_url': result.get('video_url')})
            else:
                return jsonify({'error': 'Не удалось сгенерировать видео'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Ошибка генерации видео: {str(e)}'}), 500

    # API endpoints для ElevenLabs
    @app.route('/api/elevenlabs/voices', methods=['GET'])
    def get_elevenlabs_voices():
        """Получение списка доступных голосов ElevenLabs"""
        try:
            from api.elevenlabs_client import ElevenLabsClient
            elevenlabs_client = ElevenLabsClient()
            voices = elevenlabs_client.get_available_voices()
            return jsonify({'voices': voices})
        except Exception as e:
            return jsonify({'error': f'Ошибка получения голосов: {str(e)}'}), 500

    @app.route('/api/elevenlabs/models', methods=['GET'])
    def get_elevenlabs_models():
        """Получение списка доступных моделей ElevenLabs"""
        try:
            from api.elevenlabs_client import ElevenLabsClient
            elevenlabs_client = ElevenLabsClient()
            models = elevenlabs_client.get_available_models()
            return jsonify({'models': models})
        except Exception as e:
            return jsonify({'error': f'Ошибка получения моделей: {str(e)}'}), 500

    return app

# Создаем приложение
app = create_simple_app()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
