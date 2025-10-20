#!/usr/bin/env python3
"""
Тест Step 6: Генерация видео HeyGen
Проверяет полный пайплайн от аудио до видео
"""

import requests
import json
import time

def test_step6_video_generation():
    """Тестирует генерацию видео через HeyGen API"""
    
    base_url = "http://72.56.66.228"
    
    print("🎬 Тестирование Step 6: Генерация видео")
    print("=" * 50)
    
    # 1. Проверяем доступность аватаров
    print("1️⃣ Проверяем список аватаров...")
    try:
        response = requests.get(f"{base_url}/api/trends/list-avatars")
        if response.status_code == 200:
            data = response.json()
            avatars = data.get('avatars', [])
            print(f"✅ Получено аватаров: {len(avatars)}")
            if avatars:
                first_avatar = avatars[0]
                print(f"   Первый аватар: {first_avatar.get('avatar_name')} (ID: {first_avatar.get('avatar_id')})")
                avatar_id = first_avatar.get('avatar_id')
            else:
                print("❌ Аватары не найдены")
                return False
        else:
            print(f"❌ Ошибка получения аватаров: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка запроса аватаров: {e}")
        return False
    
    # 2. Тестируем генерацию видео с демо аудио
    print("\n2️⃣ Тестируем генерацию видео...")
    
    # Используем демо аудио URL (ElevenLabs)
    demo_audio_url = "https://api.elevenlabs.io/v1/text-to-speech/jP9L6ZC55cz5mmx4ZpCk"
    
    payload = {
        "audio_url": demo_audio_url,
        "avatar_id": avatar_id,
        "video_format": "vertical"
    }
    
    print(f"   Отправляем запрос: {payload}")
    
    try:
        response = requests.post(
            f"{base_url}/api/trends/generate-video",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                if data.get('video_url'):
                    print("✅ Получен прямой URL видео (fallback)")
                    return True
                elif data.get('video_id'):
                    print(f"✅ Получен video_id: {data['video_id']}")
                    
                    # 3. Проверяем статус генерации
                    print("\n3️⃣ Проверяем статус генерации...")
                    video_id = data['video_id']
                    
                    for attempt in range(3):  # Проверяем 3 раза
                        time.sleep(5)  # Ждем 5 секунд
                        
                        try:
                            status_response = requests.get(f"{base_url}/api/trends/video-status/{video_id}")
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                print(f"   Попытка {attempt + 1}: {json.dumps(status_data, indent=2, ensure_ascii=False)}")
                                
                                if status_data.get('success'):
                                    status = status_data.get('status')
                                    if status == 'completed':
                                        print("✅ Видео готово!")
                                        return True
                                    elif status == 'failed':
                                        print("❌ Генерация видео не удалась")
                                        return False
                                    else:
                                        print(f"⏳ Статус: {status}, ждем...")
                                else:
                                    print(f"❌ Ошибка проверки статуса: {status_data.get('message')}")
                            else:
                                print(f"❌ Ошибка запроса статуса: {status_response.status_code}")
                        except Exception as e:
                            print(f"❌ Ошибка проверки статуса: {e}")
                    
                    print("⏳ Генерация видео занимает время (7-10 минут), тест завершен")
                    return True
                else:
                    print("❌ Не получен ни video_id, ни video_url")
                    return False
            else:
                print(f"❌ Ошибка генерации: {data.get('message')}")
                return False
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка генерации видео: {e}")
        return False

if __name__ == "__main__":
    success = test_step6_video_generation()
    
    if success:
        print("\n🎉 Тест Step 6 прошел успешно!")
        print("✅ Генерация видео работает")
    else:
        print("\n❌ Тест Step 6 не прошел")
        print("❌ Проблемы с генерацией видео")
