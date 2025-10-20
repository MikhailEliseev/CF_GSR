#!/usr/bin/env python3
"""
Тест ElevenLabs API локально
"""

import requests
import json

def test_elevenlabs_local():
    """Тестируем ElevenLabs API локально"""
    api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
    
    print("🧪 Тестируем ElevenLabs API локально...")
    
    try:
        # Тест 1: Проверка пользователя
        print("\n1️⃣ Проверяем пользователя...")
        response = requests.get(
            "https://api.elevenlabs.io/v1/user",
            headers={"xi-api-key": api_key},
            timeout=15
        )
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Пользователь: {user_data.get('first_name', 'N/A')}")
            print(f"✅ Подписка: {user_data.get('subscription', {}).get('tier', 'N/A')}")
            print(f"✅ Workspace: {user_data.get('workspace', {}).get('name', 'N/A')}")
        else:
            print(f"❌ Ошибка: {response.text}")
            return False
        
        # Тест 2: Получение голосов
        print("\n2️⃣ Получаем голоса...")
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": api_key},
            timeout=15
        )
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ Найдено голосов: {len(voices.get('voices', []))}")
            if voices.get('voices'):
                first_voice = voices['voices'][0]
                print(f"✅ Первый голос: {first_voice.get('name', 'N/A')} (ID: {first_voice.get('voice_id', 'N/A')})")
                
                # Тест 3: Генерация аудио
                print("\n3️⃣ Генерируем аудио...")
                payload = {
                    "text": "Привет! Это тест ElevenLabs API.",
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5
                    }
                }
                
                response = requests.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{first_voice['voice_id']}",
                    headers={
                        "xi-api-key": api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30
                )
                
                print(f"Статус: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Аудио сгенерировано! Размер: {len(response.content)} байт")
                    
                    # Сохраняем файл
                    with open("test_audio_local.mp3", "wb") as f:
                        f.write(response.content)
                    print("💾 Аудио сохранено как test_audio_local.mp3")
                    return True
                else:
                    print(f"❌ Ошибка генерации: {response.text}")
                    return False
        else:
            print(f"❌ Ошибка голосов: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут подключения")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_elevenlabs_local()
    if success:
        print("\n🎉 ElevenLabs API работает локально!")
        print("Проблема может быть в сетевых настройках сервера")
    else:
        print("\n❌ ElevenLabs API не работает локально")
        print("Возможно, проблема с API ключом или аккаунтом")
