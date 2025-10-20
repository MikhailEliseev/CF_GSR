#!/usr/bin/env python3
import requests
import time

print("🔍 Проверка сервера на http://72.56.66.228:5000/")

try:
    response = requests.get("http://72.56.66.228:5000/", timeout=10)
    print(f"✅ Сервер отвечает! Код: {response.status_code}")
    print(f"📄 Первые 200 символов ответа:")
    print(response.text[:200])
except requests.exceptions.Timeout:
    print("❌ Timeout - сервер не отвечает в течение 10 секунд")
except requests.exceptions.ConnectionError:
    print("❌ Connection Error - не удается подключиться к серверу")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n🔍 Проверка эндпоинта /api/vacancies/list-avatars")
try:
    response = requests.get("http://72.56.66.228:5000/api/vacancies/list-avatars", timeout=10)
    print(f"✅ Эндпоинт отвечает! Код: {response.status_code}")
    print(f"📄 Ответ:")
    print(response.json())
except Exception as e:
    print(f"❌ Ошибка: {e}")

