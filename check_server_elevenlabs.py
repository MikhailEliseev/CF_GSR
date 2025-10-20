#!/usr/bin/env python3
"""
Проверка ElevenLabs на сервере
"""

import paramiko
import json

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def check_server_elevenlabs():
    """Проверяем ElevenLabs на сервере"""
    print("🔍 Проверяем ElevenLabs на сервере...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # Проверяем настройки
        print("\n1️⃣ Проверяем настройки ElevenLabs...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000/api/settings/vacancies")
        settings = json.loads(stdout.read().decode())
        elevenlabs_key = settings.get('api_keys', {}).get('elevenlabs_api_key', '')
        print(f"Ключ ElevenLabs: {elevenlabs_key[:20]}...")
        
        # Проверяем логи сервера
        print("\n2️⃣ Проверяем логи сервера...")
        stdin, stdout, stderr = ssh.exec_command("tail -20 /root/server.log")
        logs = stdout.read().decode()
        print("Последние логи:")
        print(logs)
        
        # Проверяем процессы
        print("\n3️⃣ Проверяем процессы...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep python | grep -v grep")
        processes = stdout.read().decode()
        print("Python процессы:")
        print(processes)
        
        # Тестируем ElevenLabs API с сервера
        print("\n4️⃣ Тестируем ElevenLabs API с сервера...")
        test_script = '''
import requests
import json

api_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"

try:
    # Тест статуса
    response = requests.get(
        "https://api.elevenlabs.io/v1/user",
        headers={"xi-api-key": api_key},
        timeout=10
    )
    print(f"Статус API: {response.status_code}")
    if response.status_code == 200:
        print("✅ ElevenLabs API доступен")
    else:
        print(f"❌ Ошибка API: {response.text[:200]}")
        
    # Тест голосов
    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key},
        timeout=10
    )
    print(f"Статус голосов: {response.status_code}")
    if response.status_code == 200:
        voices = response.json()
        print(f"✅ Найдено голосов: {len(voices.get('voices', []))}")
    else:
        print(f"❌ Ошибка голосов: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
'''
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"{test_script}\"")
        result = stdout.read().decode()
        print("Результат теста:")
        print(result)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_server_elevenlabs()
