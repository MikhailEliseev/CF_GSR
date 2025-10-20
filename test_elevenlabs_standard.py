#!/usr/bin/env python3
"""Тест со стандартными голосами ElevenLabs"""

import requests
import json

def test_standard_voices():
    """Тестируем стандартные голоса"""
    
    # Новый ключ
    api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
    
    # Стандартные голоса ElevenLabs
    standard_voices = [
        "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "AZnzlk1XvdvUeBnXmlld",  # Domi
        "EXAVITQu4vr4xnSDxMaL",  # Bella
        "MF3mGyEYCl7XYWbV9V6O",  # Elli
        "TxGEqnHWrfWFTfGW9XjX",  # Josh
        "VR6AewLTigWG4xSOukaG",  # Arnold
        "pNInz6obpgDQGcFmaJgB",  # Adam
        "yoZ06aMxZJJ28mfd3POQ",  # Sam
    ]
    
    for voice_id in standard_voices:
        print(f"\n🎤 Тестируем голос: {voice_id}")
        
        # URL для генерации аудио
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        # Заголовки
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        # Данные для запроса
        data = {
            "text": "Hello, this is a test",
            "model_id": "eleven_monolingual_v1"
        }
        
        try:
            # Отправляем запрос
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            print(f"📊 Статус: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Голос {voice_id} работает!")
                
                # Сохраняем аудио в файл
                filename = f"test_audio_{voice_id}.mp3"
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"💾 Аудио сохранено в {filename}")
                
                return voice_id
            else:
                print(f"❌ Голос {voice_id} не работает: {response.status_code}")
                print(f"📄 Ответ: {response.text}")
                
        except Exception as e:
            print(f"❌ Ошибка для голоса {voice_id}: {e}")
    
    return None

if __name__ == "__main__":
    print("🎵 Тестируем стандартные голоса ElevenLabs...")
    working_voice = test_standard_voices()
    
    if working_voice:
        print(f"🎉 Найден рабочий голос: {working_voice}")
    else:
        print("💥 Ни один голос не работает!")
