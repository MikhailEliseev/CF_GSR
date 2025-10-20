#!/usr/bin/env python3
"""Прямой тест ElevenLabs API"""

import requests
import json

def test_elevenlabs_api():
    """Тестируем ElevenLabs API напрямую"""
    
    # Новый ключ
    api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
    
    # URL для генерации аудио
    url = "https://api.elevenlabs.io/v1/text-to-speech/jP9L6ZC55cz5mmx4ZpCk"
    
    # Заголовки
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Данные для запроса
    data = {
        "text": "Привет, это тест генерации аудио",
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    print(f"🔑 Тестируем ключ: {api_key[:20]}...")
    print(f"🌐 URL: {url}")
    print(f"📝 Текст: {data['text']}")
    
    try:
        # Отправляем запрос
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Статус: {response.status_code}")
        print(f"📏 Размер ответа: {len(response.content)} байт")
        
        if response.status_code == 200:
            print("✅ ElevenLabs API работает!")
            
            # Сохраняем аудио в файл
            with open("test_audio.mp3", "wb") as f:
                f.write(response.content)
            print("💾 Аудио сохранено в test_audio.mp3")
            
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
    print("🎵 Тестируем ElevenLabs API...")
    success = test_elevenlabs_api()
    
    if success:
        print("🎉 Тест прошел успешно!")
    else:
        print("💥 Тест не прошел!")
