#!/usr/bin/env python3
"""
Детальная диагностика ElevenLabs API
"""

import paramiko
import json

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def debug_elevenlabs():
    """Детальная диагностика ElevenLabs"""
    print("🔍 Детальная диагностика ElevenLabs...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Проверяем сетевую доступность
        print("\n1️⃣ Проверяем сетевую доступность...")
        stdin, stdout, stderr = ssh.exec_command("curl -I https://api.elevenlabs.io/v1/user")
        curl_result = stdout.read().decode()
        print("Результат curl:")
        print(curl_result)
        
        # 2. Проверяем с User-Agent
        print("\n2️⃣ Проверяем с User-Agent...")
        stdin, stdout, stderr = ssh.exec_command("curl -H 'User-Agent: Mozilla/5.0' -I https://api.elevenlabs.io/v1/user")
        curl_ua_result = stdout.read().decode()
        print("Результат curl с User-Agent:")
        print(curl_ua_result)
        
        # 3. Тестируем с Python requests
        print("\n3️⃣ Тестируем с Python requests...")
        test_script = '''
import requests
import json
import sys

api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"

print("=== Детальный тест ElevenLabs API ===")

try:
    # Настройки для обхода Cloudflare
    headers = {
        "xi-api-key": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    print("1. Тестируем /v1/user...")
    response = requests.get(
        "https://api.elevenlabs.io/v1/user",
        headers=headers,
        timeout=20,
        allow_redirects=True
    )
    
    print(f"Статус: {response.status_code}")
    print(f"Заголовки: {dict(response.headers)}")
    print(f"Текст ответа: {response.text[:500]}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Пользователь: {user_data.get('first_name', 'N/A')}")
        print(f"✅ Подписка: {user_data.get('subscription', {}).get('tier', 'N/A')}")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        
    print("\\n2. Тестируем /v1/voices...")
    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers=headers,
        timeout=20,
        allow_redirects=True
    )
    
    print(f"Статус: {response.status_code}")
    print(f"Текст ответа: {response.text[:500]}")
    
    if response.status_code == 200:
        voices = response.json()
        print(f"✅ Голосов: {len(voices.get('voices', []))}")
    else:
        print(f"❌ Ошибка голосов: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ Таймаут подключения")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Ошибка подключения: {e}")
except Exception as e:
    print(f"❌ Общая ошибка: {e}")
    import traceback
    traceback.print_exc()
'''
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"{test_script}\"")
        result = stdout.read().decode()
        print("Результат детального теста:")
        print(result)
        
        # 4. Проверяем альтернативные endpoints
        print("\n4️⃣ Проверяем альтернативные endpoints...")
        stdin, stdout, stderr = ssh.exec_command("curl -s https://api.elevenlabs.io/v1/models")
        models_result = stdout.read().decode()
        print("Модели:")
        print(models_result[:200])
        
    except Exception as e:
        print(f"❌ Ошибка диагностики: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    debug_elevenlabs()
