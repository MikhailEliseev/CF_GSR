#!/usr/bin/env python3
"""Прямой тест backend генерации аудио"""

import sys
import os
sys.path.insert(0, '/root')

# Устанавливаем переменные окружения
os.environ['ELEVENLABS_API_KEY'] = 'sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828'

from api.elevenlabs_simple import ElevenLabsSimple

def test_direct_generation():
    print("🧪 === ПРЯМОЙ ТЕСТ BACKEND ===")
    
    # Создаем клиент
    key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
    print(f"🔑 Создаем клиент с ключом: {key[:20]}...")
    client = ElevenLabsSimple(key)
    
    # Тестируем генерацию
    print("🎵 Вызываем generate_audio...")
    text = "Привет! Тест прямого вызова"
    voice_id = "CfPkL4eEqBDVYldLZuY5"  # Русский голос
    model_id = "eleven_multilingual_v2"
    
    print(f"📝 Текст: {text}")
    print(f"🎤 Voice: {voice_id}")
    print(f"🤖 Model: {model_id}")
    
    try:
        url = client.generate_audio(
            text=text, 
            voice_id=voice_id,
            model_id=model_id
        )
        print(f"✅ Результат: {url}")
        
        if url and not url.endswith('test_hello.mp3'):
            print("🎉 УСПЕХ! Получено реальное аудио!")
        else:
            print("❌ ПРОВАЛ! Получена заглушка test_hello.mp3")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_generation()
