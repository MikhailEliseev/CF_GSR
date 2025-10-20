#!/usr/bin/env python3
"""
Скрипт для обновления сервера 72.56.66.228
"""

import requests
import json

def update_server():
    """Обновляем код на сервере через API"""
    
    # URL сервера
    server_url = "http://72.56.66.228"
    
    print("🔄 Обновляем сервер...")
    
    # 1. Обновляем HeyGen API ключ
    print("1️⃣ Обновляем HeyGen API ключ...")
    try:
        response = requests.post(f"{server_url}/api/settings/vacancies", 
                               json={
                                   "api_keys": {
                                       "heygen_api_key": "ZjI2NmI4MGEzOTA0NDIwNzgxNjIzMjdjOWU0N2E3YWEtMTc2MDUxOTU5OQ=="
                                   }
                               })
        if response.status_code == 200:
            print("✅ HeyGen API ключ обновлен")
        else:
            print(f"❌ Ошибка обновления API ключа: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # 2. Проверяем статус API
    print("2️⃣ Проверяем статус API...")
    try:
        response = requests.post(f"{server_url}/api/vacancies/check-video-status", 
                               json={"video_id": "test"})
        if response.status_code == 200:
            data = response.json()
            if "HeyGenClient" in str(data):
                print("❌ Сервер все еще использует старую версию кода")
                print("💡 Нужно обновить код на сервере вручную")
            else:
                print("✅ API работает корректно")
        else:
            print(f"❌ Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # 3. Тестируем полный пайплайн
    print("3️⃣ Тестируем полный пайплайн...")
    try:
        # Загружаем тестовые данные
        response = requests.get(f"{server_url}/api/vacancies/test")
        if response.status_code == 200:
            print("✅ Тестовые данные загружаются")
        else:
            print(f"❌ Ошибка загрузки тестовых данных: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    update_server()
