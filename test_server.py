#!/usr/bin/env python3
"""Простой тестовый сервер для проверки аудио генерации"""

import os
import sys
sys.path.insert(0, '/root')

from flask import Flask, request, jsonify
from api.elevenlabs_simple import ElevenLabsSimple

app = Flask(__name__)

@app.route('/api/vacancies/generate-audio', methods=['POST'])
def generate_audio():
    print("🎵 === ТЕСТОВЫЙ СЕРВЕР generate_audio ===")
    
    try:
        data = request.get_json() or {}
        text = (data.get('text') or '').strip()
        print(f"📝 Текст: {text[:50]}...")
        
        if not text:
            return jsonify({'success': False, 'message': 'Текст не передан'}), 400
        
        # Создаем клиент
        key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
        print(f"🔑 Ключ: {key[:20]}...")
        
        client = ElevenLabsSimple(key)
        print(f"🎤 Клиент создан")
        
        # Генерируем аудио
        voice_id = "CfPkL4eEqBDVYldLZuY5"  # Русский голос
        model_id = "eleven_multilingual_v2"
        
        print(f"🎵 Генерируем аудио с voice={voice_id}, model={model_id}")
        audio_url = client.generate_audio(text, voice_id=voice_id, model_id=model_id)
        
        print(f"🎧 Результат: {audio_url}")
        
        return jsonify({'success': True, 'audio_url': audio_url})
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Запускаем тестовый сервер на порту 5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
