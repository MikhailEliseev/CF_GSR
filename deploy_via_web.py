#!/usr/bin/env python3
"""
Скрипт для деплоя изменений через веб-интерфейс
"""

import requests
import json
import base64
import time

def test_server_connection():
    """Тестирует подключение к серверу"""
    try:
        response = requests.get("http://72.56.66.228:5000/", timeout=10)
        if response.status_code == 200:
            print("✅ Сервер доступен")
            return True
        else:
            print(f"❌ Сервер недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к серверу: {e}")
        return False

def test_new_endpoint():
    """Тестирует новый endpoint для аватаров"""
    try:
        response = requests.get("http://72.56.66.228:5000/api/vacancies/list-avatars", timeout=10)
        if response.status_code == 200:
            print("✅ Новый endpoint работает")
            return True
        else:
            print(f"⚠️ Endpoint не найден: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка тестирования endpoint: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Тестируем подключение к серверу...")
    
    if not test_server_connection():
        print("❌ Не удалось подключиться к серверу")
        return
    
    print("🔍 Проверяем новый endpoint...")
    if test_new_endpoint():
        print("✅ Изменения уже применены!")
    else:
        print("⚠️ Изменения еще не применены")
        print("📝 Необходимо обновить файлы на сервере вручную:")
        print("   1. config.py - обновлённый API ключ HeyGen")
        print("   2. app_current_backup.py - новый endpoint /api/vacancies/list-avatars")
        print("   3. templates/module_vacancies.html - обновлённый HTML с выбором аватаров")
        print("   4. routes/vacancies.py - обновлённая логика генерации видео")
        print("\n🔄 После обновления файлов перезапустите сервер")

if __name__ == "__main__":
    main()
