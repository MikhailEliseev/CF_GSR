#!/usr/bin/env python3
"""
Тест генерации аудио
"""

import requests
import json

def test_audio_generation():
    """Тестируем генерацию аудио"""
    print("🧪 Тестируем генерацию аудио...")
    
    try:
        # Тест 1: Проверяем доступность страницы
        print("\n1️⃣ Проверяем доступность страницы...")
        response = requests.get("http://72.56.66.228/module/vacancies")
        if response.status_code == 200:
            print("✅ Страница доступна")
        else:
            print(f"❌ Страница недоступна: {response.status_code}")
            return False
        
        # Тест 2: Проверяем настройки ElevenLabs
        print("\n2️⃣ Проверяем настройки ElevenLabs...")
        response = requests.get("http://72.56.66.228/api/settings/vacancies")
        if response.status_code == 200:
            settings = response.json()
            elevenlabs_key = settings.get('api_keys', {}).get('elevenlabs_api_key', '')
            print(f"✅ ElevenLabs ключ: {elevenlabs_key[:20]}...")
        else:
            print(f"❌ Настройки недоступны: {response.status_code}")
            return False
        
        # Тест 3: Проверяем генерацию текста
        print("\n3️⃣ Проверяем генерацию текста...")
        text_payload = {
            "vacancy": {
                "position": "Тестовая вакансия",
                "location": "Москва",
                "salary": "50000 руб",
                "conditions": "Полный день",
                "requirements": "Опыт работы",
                "benefits": "Социальный пакет"
            }
        }
        
        response = requests.post(
            "http://72.56.66.228/api/vacancies/generate-text",
            headers={"Content-Type": "application/json"},
            json=text_payload
        )
        
        if response.status_code == 200:
            text_data = response.json()
            if text_data.get('success'):
                print("✅ Текст сгенерирован")
                generated_text = text_data.get('text', '')
                print(f"Текст: {generated_text[:100]}...")
                
                # Тест 4: Проверяем генерацию аудио
                print("\n4️⃣ Проверяем генерацию аудио...")
                audio_payload = {
                    "text": generated_text
                }
                
                response = requests.post(
                    "http://72.56.66.228/api/vacancies/generate-audio",
                    headers={"Content-Type": "application/json"},
                    json=audio_payload
                )
                
                if response.status_code == 200:
                    audio_data = response.json()
                    if audio_data.get('success'):
                        print("✅ Аудио сгенерировано через ElevenLabs")
                        return True
                    else:
                        print(f"❌ Ошибка генерации аудио: {audio_data.get('error', 'Неизвестная ошибка')}")
                        
                        # Пробуем fallback
                        print("\n5️⃣ Пробуем fallback...")
                        response = requests.post(
                            "http://72.56.66.228/api/vacancies/generate-audio-fallback",
                            headers={"Content-Type": "application/json"},
                            json=audio_payload
                        )
                        
                        if response.status_code == 200:
                            fallback_data = response.json()
                            if fallback_data.get('success'):
                                print("✅ Аудио сгенерировано через fallback")
                                return True
                            else:
                                print(f"❌ Fallback не работает: {fallback_data.get('error', 'Неизвестная ошибка')}")
                        else:
                            print(f"❌ Fallback недоступен: {response.status_code}")
                        
                        return False
                else:
                    print(f"❌ Ошибка запроса аудио: {response.status_code}")
                    return False
            else:
                print(f"❌ Ошибка генерации текста: {text_data.get('error', 'Неизвестная ошибка')}")
                return False
        else:
            print(f"❌ Ошибка запроса текста: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_audio_generation()
    if success:
        print("\n🎉 Генерация аудио работает!")
    else:
        print("\n❌ Проблема с генерацией аудио")
        print("Возможные причины:")
        print("1. ElevenLabs API заблокирован Cloudflare")
        print("2. Fallback не настроен")
        print("3. Проблемы с сервером")
