#!/usr/bin/env python3
"""
Тестирование ElevenLabs API
"""

import requests
import json

def test_elevenlabs_api():
    """Тестируем ElevenLabs API"""
    api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
    
    print("🧪 Тестируем ElevenLabs API...")
    
    # Тест 1: Проверяем статус API
    print("\n1️⃣ Проверяем статус API...")
    try:
        response = requests.get(
            "https://api.elevenlabs.io/v1/user",
            headers={"xi-api-key": api_key}
        )
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ API ключ валиден")
            print(f"Пользователь: {user_data.get('first_name', 'N/A')}")
            print(f"Подписка: {user_data.get('subscription', {}).get('tier', 'N/A')}")
        else:
            print(f"❌ Ошибка API: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    # Тест 2: Получаем список голосов
    print("\n2️⃣ Получаем список голосов...")
    try:
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": api_key}
        )
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ Найдено голосов: {len(voices.get('voices', []))}")
            if voices.get('voices'):
                first_voice = voices['voices'][0]
                print(f"Первый голос: {first_voice.get('name', 'N/A')} (ID: {first_voice.get('voice_id', 'N/A')})")
        else:
            print(f"❌ Ошибка получения голосов: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка получения голосов: {e}")
        return False
    
    # Тест 3: Пробуем сгенерировать короткий аудио
    print("\n3️⃣ Тестируем генерацию аудио...")
    try:
        # Используем первый доступный голос
        voice_id = voices['voices'][0]['voice_id']
        
        payload = {
            "text": "Привет! Это тест ElevenLabs API.",
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Аудио сгенерировано успешно!")
            print(f"Размер аудио: {len(response.content)} байт")
            
            # Сохраняем тестовый файл
            with open("test_audio.mp3", "wb") as f:
                f.write(response.content)
            print("💾 Аудио сохранено как test_audio.mp3")
        else:
            print(f"❌ Ошибка генерации аудио: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка генерации аудио: {e}")
        return False
    
    print("\n🎉 Все тесты ElevenLabs прошли успешно!")
    return True

if __name__ == "__main__":
    test_elevenlabs_api()
