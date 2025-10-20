#!/usr/bin/env python3
"""
Простой тест ElevenLabs
"""

import requests
import json

def test_simple():
    """Простой тест ElevenLabs API"""
    api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
    
    print("🧪 Простой тест ElevenLabs...")
    
    try:
        # Тест 1: Получаем голоса
        print("1️⃣ Получаем голоса...")
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": api_key},
            timeout=10
        )
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ Голосов: {len(voices.get('voices', []))}")
            
            if voices.get('voices'):
                voice = voices['voices'][0]
                print(f"✅ Первый голос: {voice.get('name')} (ID: {voice.get('voice_id')})")
                
                # Тест 2: Генерируем аудио
                print("\n2️⃣ Генерируем аудио...")
                payload = {
                    "text": "Привет! Это тест.",
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5
                    }
                }
                
                response = requests.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice['voice_id']}",
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
                    with open("test_audio.mp3", "wb") as f:
                        f.write(response.content)
                    print("💾 Аудио сохранено как test_audio.mp3")
                    return True
                else:
                    print(f"❌ Ошибка генерации: {response.text}")
                    return False
        else:
            print(f"❌ Ошибка получения голосов: {response.text}")
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
    success = test_simple()
    if success:
        print("\n🎉 ElevenLabs работает!")
    else:
        print("\n❌ ElevenLabs не работает!")
