#!/usr/bin/env python3
"""Проверяем доступные голоса ElevenLabs"""

import requests
import json

def check_elevenlabs_voices():
    """Проверяем доступные голоса"""
    
    # Новый ключ
    api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
    
    # URL для получения голосов
    url = "https://api.elevenlabs.io/v1/voices"
    
    # Заголовки
    headers = {
        "xi-api-key": api_key
    }
    
    print(f"🔑 Проверяем ключ: {api_key[:20]}...")
    print(f"🌐 URL: {url}")
    
    try:
        # Отправляем запрос
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ Найдено голосов: {len(voices.get('voices', []))}")
            
            print("\n🎤 Доступные голоса:")
            for voice in voices.get('voices', []):
                print(f"  - {voice.get('name', 'Unknown')} (ID: {voice.get('voice_id', 'Unknown')})")
            
            return voices.get('voices', [])
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return []
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return []

if __name__ == "__main__":
    print("🎵 Проверяем доступные голоса ElevenLabs...")
    voices = check_elevenlabs_voices()
    
    if voices:
        print(f"🎉 Найдено {len(voices)} голосов!")
    else:
        print("💥 Не удалось получить голоса!")
