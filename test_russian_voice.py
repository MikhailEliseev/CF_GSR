#!/usr/bin/env python3
"""Тест русского голоса Алексей Архангельский"""

import requests
import json

def test_russian_voice():
    """Тестируем русский голос"""
    
    # Ключ с исправленными правами
    api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
    
    # Русский голос
    voice_id = "CfPkL4eEqBDVYldLZuY5"  # Алексей Архангельский
    
    # URL для генерации аудио
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    # Заголовки
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Данные для запроса
    data = {
        "text": "Привет! Это тест русского голоса Алексея Архангельского. Как дела?",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    print(f"🔑 Тестируем ключ: {api_key[:20]}...")
    print(f"🎤 Голос: Алексей Архангельский ({voice_id})")
    print(f"🌐 URL: {url}")
    print(f"📝 Текст: {data['text']}")
    
    try:
        # Отправляем запрос
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Статус: {response.status_code}")
        print(f"📏 Размер ответа: {len(response.content)} байт")
        
        if response.status_code == 200:
            print("✅ Русский голос работает!")
            
            # Сохраняем аудио в файл
            with open("test_russian_voice.mp3", "wb") as f:
                f.write(response.content)
            print("💾 Аудио сохранено в test_russian_voice.mp3")
            
            return True
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🎵 Тестируем русский голос Алексей Архангельский...")
    success = test_russian_voice()
    
    if success:
        print("🎉 Тест прошел успешно!")
    else:
        print("💥 Тест не прошел!")
