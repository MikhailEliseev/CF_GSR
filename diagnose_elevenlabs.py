#!/usr/bin/env python3
"""
Диагностика проблем с ElevenLabs
"""

import paramiko
import time

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def diagnose_elevenlabs():
    """Диагностируем проблемы с ElevenLabs"""
    print("🔍 Диагностика ElevenLabs...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Проверяем доступность ElevenLabs API
        print("\n1️⃣ Проверяем доступность ElevenLabs API...")
        test_cmd = '''
import requests
import json

api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"

print("Тестируем ElevenLabs API...")

try:
    # Тест 1: Проверка статуса
    print("Тест 1: Проверка статуса пользователя...")
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
    else:
        print(f"❌ Ошибка: {response.text[:200]}")
        
    # Тест 2: Получение голосов
    print("\\nТест 2: Получение голосов...")
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
            print(f"✅ Первый голос: {first_voice.get('name', 'N/A')}")
    else:
        print(f"❌ Ошибка: {response.text[:200]}")
        
    # Тест 3: Генерация аудио
    print("\\nТест 3: Генерация аудио...")
    if voices.get('voices'):
        voice_id = voices['voices'][0]['voice_id']
        payload = {
            "text": "Привет! Это тест.",
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
            json=payload,
            timeout=30
        )
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Аудио сгенерировано! Размер: {len(response.content)} байт")
        else:
            print(f"❌ Ошибка генерации: {response.text[:200]}")
    
except requests.exceptions.Timeout:
    print("❌ Таймаут подключения к ElevenLabs")
except requests.exceptions.ConnectionError:
    print("❌ Ошибка подключения к ElevenLabs")
except Exception as e:
    print(f"❌ Общая ошибка: {e}")
'''
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"{test_cmd}\"")
        result = stdout.read().decode()
        print("Результат теста:")
        print(result)
        
        # 2. Проверяем логи приложения
        print("\n2️⃣ Проверяем логи приложения...")
        stdin, stdout, stderr = ssh.exec_command("tail -50 /root/server.log | grep -i elevenlabs")
        logs = stdout.read().decode()
        if logs.strip():
            print("Логи ElevenLabs:")
            print(logs)
        else:
            print("Нет логов ElevenLabs в последних 50 строках")
        
        # 3. Проверяем сетевую доступность
        print("\n3️⃣ Проверяем сетевую доступность...")
        stdin, stdout, stderr = ssh.exec_command("curl -I https://api.elevenlabs.io/v1/user")
        curl_result = stdout.read().decode()
        print("Результат curl:")
        print(curl_result)
        
    except Exception as e:
        print(f"❌ Ошибка диагностики: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    diagnose_elevenlabs()
