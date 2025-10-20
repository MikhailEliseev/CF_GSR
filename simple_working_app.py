#!/usr/bin/env python3
"""
МАКСИМАЛЬНО ПРОСТАЯ РАБОЧАЯ ВЕРСИЯ
Без сложной логики, только базовый функционал
"""

from flask import Flask, render_template, request, jsonify
import os
import json

# Создаем приложение Flask
app = Flask(__name__)

# Конфигурация
app.config['SECRET_KEY'] = 'gsr-secret-key-2025'

# Главная страница
@app.route('/')
def index():
    return render_template('index_clean.html')

# Модули
@app.route('/module/trends')
def module_trends():
    return render_template('module_trends_clean.html')

@app.route('/module/experts')
def module_experts():
    return render_template('module_experts_clean.html')

@app.route('/module/vacancies')
def module_vacancies():
    return render_template('module_vacancies.html')

# API endpoints - простые заглушки
@app.route('/api/experts/generate-topics', methods=['POST'])
def generate_topics():
    """Генерация тем для экспертов"""
    try:
        data = request.json
        num_topics = data.get('num_topics', 5)
        
        # Простые демо темы
        topics = [
            f"{i+1}. Как правильно {['вести бизнес', 'управлять командой', 'планировать бюджет', 'развивать продукт', 'работать с клиентами'][i % 5]}"
            for i in range(num_topics)
        ]
        
        return jsonify({
            'success': True,
            'topics': topics,
            'message': f'{num_topics} тем успешно сгенерированы'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/experts/generate-text', methods=['POST'])
def generate_text():
    """Генерация текста для экспертов"""
    try:
        data = request.json
        topic = data.get('topic', 'Общая тема')
        
        # Простой демо текст
        text = f"""
        Добро пожаловать в мир экспертизы! Сегодня мы поговорим о теме: "{topic}".
        
        Это важная тема, которая поможет вам развиваться и достигать новых высот.
        В этом видео мы рассмотрим основные принципы и дадим практические советы.
        
        Не забудьте подписаться на наш канал для получения новых экспертных материалов!
        """
        
        return jsonify({
            'success': True,
            'text': text.strip(),
            'message': 'Текст успешно сгенерирован'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/experts/generate-audio', methods=['POST'])
def generate_audio():
    """Генерация аудио для экспертов"""
    try:
        data = request.json
        text = data.get('text', '')
        
        # Создаем простой аудио файл
        import uuid
        audio_filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        audio_url = f"/static/audio/{audio_filename}"
        
        # Создаем директорию если не существует
        os.makedirs('static/audio', exist_ok=True)
        
        # Создаем простой MP3 файл (заглушка)
        with open(f'static/audio/{audio_filename}', 'wb') as f:
            # Простой MP3 заголовок
            f.write(b'\xff\xfb\x90\x00' + b'\x00' * 1000)
        
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'message': 'Аудио успешно создано'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/experts/generate-video', methods=['POST'])
def generate_video():
    """Генерация видео для экспертов"""
    try:
        data = request.json
        text = data.get('text', '')
        audio_url = data.get('audio_url', '')
        
        # Простой ответ
        return jsonify({
            'success': True,
            'video_url': 'https://example.com/video.mp4',
            'message': 'Видео успешно создано'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API для вакансий
@app.route('/api/vacancies/parse', methods=['POST'])
def parse_vacancies():
    """Парсинг вакансий"""
    try:
        data = request.json
        url = data.get('csv_url', data.get('url', ''))
        
        # Простые демо вакансии
        vacancies = [
            {
                'position': 'Менеджер по продажам',
                'company': 'ООО "Компания"',
                'location': 'Москва',
                'salary': '80,000 - 120,000 руб.',
                'requirements': 'Опыт работы от 2 лет'
            },
            {
                'position': 'Разработчик Python',
                'company': 'IT Компания',
                'location': 'Санкт-Петербург',
                'salary': '150,000 - 200,000 руб.',
                'requirements': 'Знание Python, Django, PostgreSQL'
            }
        ]
        
        return jsonify({
            'success': True,
            'vacancies': vacancies,
            'message': f'Загружено {len(vacancies)} вакансий'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API для трендов
@app.route('/api/trends/collect-reels', methods=['POST'])
def collect_reels():
    """Сбор рилсов"""
    try:
        data = request.json
        usernames = data.get('usernames', [])
        count = data.get('count', 10)
        
        # Простые демо рилсы
        reels = [
            {
                'id': f'reel_{i}',
                'username': f'user_{i}',
                'views': 1000 + i * 100,
                'likes': 50 + i * 10,
                'caption': f'Интересный контент #{i}',
                'url': f'https://instagram.com/p/example{i}'
            }
            for i in range(min(count, 5))
        ]
        
        return jsonify({
            'success': True,
            'reels': reels,
            'message': f'Собрано {len(reels)} рилсов'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
