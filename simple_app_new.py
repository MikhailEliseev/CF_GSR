from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import traceback
from datetime import datetime

# Создаем приложение Flask
app = Flask(__name__)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gsr_content_factory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gsr-secret-key-2025'

# Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Модели базы данных
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False, unique=True)
    master_prompt = db.Column(db.Text, nullable=True)
    openai_api_key = db.Column(db.String(500), nullable=True)
    elevenlabs_api_key = db.Column(db.String(500), nullable=True)
    heygen_api_key = db.Column(db.String(500), nullable=True)
    apify_api_key = db.Column(db.String(500), nullable=True)
    gemini_api_key = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_api_keys(self):
        return {
            'openai_api_key': self.openai_api_key,
            'elevenlabs_api_key': self.elevenlabs_api_key,
            'heygen_api_key': self.heygen_api_key,
            'apify_api_key': self.apify_api_key,
            'gemini_api_key': self.gemini_api_key
        }

# Создание таблиц
with app.app_context():
    db.create_all()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страницы модулей
@app.route('/module/trends')
def trends_page():
    return render_template('module_trends_new.html')

@app.route('/module/vacancies')
def vacancies_page():
    return render_template('module_vacancies.html')

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

@app.route('/module/monitoring')
def module_monitoring():
    return render_template('module_monitoring.html')

# API endpoints для экспертов 2.0
@app.route('/api/experts-2-0/generate-topics', methods=['POST'])
def generate_experts_2_0_topics():
    """Генерация 50 тем через OpenAI Assistant"""
    try:
        data = request.json
        num_topics = data.get('num_topics', 50)
        
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
            # Парсим ответ и извлекаем темы
            topics = [line.strip() for line in result.split('\n') if line.strip()]
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
                "Что делать, если сломался телефон, а деньги нужны срочно"
            ]
            
            topics = demo_topics[:num_topics]
            return jsonify({
                'topics': topics,
                'message': f'Использованы демо-темы (OpenAI недоступен)'
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
        
        from api.elevenlabs_client import ElevenLabsClient
        elevenlabs_client = ElevenLabsClient()
        result = elevenlabs_client.generate_audio(text, voice_id, model_id)
        
        if result:
            return jsonify({
                'audio_url': result,
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
        audio_url = data.get('audio_url', '')
        avatar_id = data.get('avatar_id', 'default_avatar')
        
        if not audio_url:
            return jsonify({'error': 'Аудио не предоставлено'}), 400
        
        from api.heygen_client import HeyGenClient
        heygen_client = HeyGenClient()
        result = heygen_client.generate_video_complete(audio_url)
        
        if result.get('success'):
            return jsonify({
                'video_url': result.get('video_url'),
                'message': 'Видео успешно создано'
            })
        else:
            return jsonify({'error': 'Не удалось сгенерировать видео'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации видео: {str(e)}'}), 500

# API endpoints для экспертов (перенаправляем на experts-2-0)
@app.route('/api/experts/generate-topics', methods=['POST'])
def generate_expert_topics():
    return generate_experts_2_0_topics()

@app.route('/api/experts/generate-text', methods=['POST'])
def generate_expert_text():
    return generate_experts_2_0_text()

@app.route('/api/experts/generate-audio', methods=['POST'])
def generate_expert_audio():
    return generate_experts_2_0_audio()

@app.route('/api/experts/generate-video', methods=['POST'])
def generate_expert_video():
    return generate_experts_2_0_video()

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

# API endpoints для HeyGen
@app.route('/api/heygen/avatars', methods=['GET'])
def get_heygen_avatars():
    """Получение списка доступных аватаров HeyGen"""
    try:
        from api.heygen_client import HeyGenClient
        heygen_client = HeyGenClient()
        avatars = heygen_client.get_available_avatars()
        return jsonify({'avatars': avatars})
    except Exception as e:
        return jsonify({'error': f'Ошибка получения аватаров: {str(e)}'}), 500

# Настройки
@app.route('/settings/<module_name>')
def settings_page(module_name):
    settings = Settings.query.filter_by(module_name=module_name).first()
    if not settings:
        settings = Settings(module_name=module_name)
        db.session.add(settings)
        db.session.commit()
    return render_template('settings.html', settings=settings, module_name=module_name)

@app.route('/api/settings/<module_name>', methods=['POST'])
def manage_settings(module_name):
    try:
        settings = Settings.query.filter_by(module_name=module_name).first()
        if not settings:
            settings = Settings(module_name=module_name)
            db.session.add(settings)
        
        data = request.json
        settings.master_prompt = data.get('master_prompt', '')
        settings.openai_api_key = data.get('openai_api_key', '')
        settings.elevenlabs_api_key = data.get('elevenlabs_api_key', '')
        settings.heygen_api_key = data.get('heygen_api_key', '')
        settings.apify_api_key = data.get('apify_api_key', '')
        settings.gemini_api_key = data.get('gemini_api_key', '')
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Настройки сохранены'})
    except Exception as e:
        return jsonify({'error': f'Ошибка сохранения настроек: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
