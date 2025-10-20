#!/usr/bin/env python3
"""
Обновление ElevenLabs API ключа на сервере
"""

import paramiko
import json
import time

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def update_elevenlabs_key():
    """Обновляем ElevenLabs API ключ"""
    print("🔑 Обновляем ElevenLabs API ключ...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Получаем текущие настройки
        print("\n1️⃣ Получаем текущие настройки...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000/api/settings/vacancies")
        current_settings_str = stdout.read().decode().strip()
        
        try:
            current_settings = json.loads(current_settings_str)
        except json.JSONDecodeError:
            print(f"❌ Ошибка парсинга настроек: {current_settings_str}")
            return False
        
        print(f"Текущий ключ ElevenLabs: {current_settings.get('api_keys', {}).get('elevenlabs_api_key', 'НЕТ')[:20]}...")
        
        # 2. Обновляем ключ
        print("\n2️⃣ Обновляем ключ...")
        new_key = "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
        
        api_keys = current_settings.get("api_keys", {})
        additional_settings = current_settings.get("additional_settings", {})
        
        api_keys["elevenlabs_api_key"] = new_key
        
        update_payload = {
            "module_name": "vacancies",
            "api_keys": api_keys,
            "additional_settings": additional_settings
        }
        
        print("🔑 Отправляем обновление...")
        update_cmd = f"curl -X POST -H 'Content-Type: application/json' -d '{json.dumps(update_payload)}' http://localhost:5000/api/settings/vacancies"
        stdin, stdout, stderr = ssh.exec_command(update_cmd)
        update_result = stdout.read().decode().strip()
        print(f"Результат обновления: {update_result}")
        
        # 3. Проверяем что ключ обновился
        print("\n3️⃣ Проверяем обновление...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000/api/settings/vacancies")
        updated_settings_str = stdout.read().decode().strip()
        updated_settings = json.loads(updated_settings_str)
        
        updated_api_keys = updated_settings.get("api_keys", {})
        if updated_api_keys.get("elevenlabs_api_key") == new_key:
            print(f"✅ Ключ обновлен: {updated_api_keys.get('elevenlabs_api_key')[:20]}...")
        else:
            print("❌ Ключ не обновился!")
            return False
        
        # 4. Тестируем ElevenLabs API с сервера
        print("\n4️⃣ Тестируем ElevenLabs API...")
        test_script = f'''
import requests
import json

api_key = "{new_key}"

try:
    print("Тестируем ElevenLabs API...")
    
    # Тест 1: Проверка пользователя
    response = requests.get(
        "https://api.elevenlabs.io/v1/user",
        headers={{"xi-api-key": api_key}},
        timeout=15
    )
    print(f"Статус пользователя: {{response.status_code}}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Пользователь: {{user_data.get('first_name', 'N/A')}}")
        print(f"✅ Подписка: {{user_data.get('subscription', {{}}).get('tier', 'N/A')}}")
    else:
        print(f"❌ Ошибка пользователя: {{response.text[:200]}}")
        exit(1)
    
    # Тест 2: Получение голосов
    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={{"xi-api-key": api_key}},
        timeout=15
    )
    print(f"Статус голосов: {{response.status_code}}")
    if response.status_code == 200:
        voices = response.json()
        print(f"✅ Найдено голосов: {{len(voices.get('voices', []))}}")
        if voices.get('voices'):
            first_voice = voices['voices'][0]
            print(f"✅ Первый голос: {{first_voice.get('name', 'N/A')}} (ID: {{first_voice.get('voice_id', 'N/A')}})")
    else:
        print(f"❌ Ошибка голосов: {{response.text[:200]}}")
        exit(1)
    
    print("🎉 ElevenLabs API работает!")
    
except Exception as e:
    print(f"❌ Ошибка: {{e}}")
    exit(1)
'''
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"{test_script}\"")
        result = stdout.read().decode()
        print("Результат теста:")
        print(result)
        
        if "✅" in result and "работает" in result:
            print("\n🎉 ElevenLabs API работает с новым ключом!")
            return True
        else:
            print("\n❌ ElevenLabs API все еще не работает")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    success = update_elevenlabs_key()
    if success:
        print("\n✅ ElevenLabs ключ обновлен и работает!")
        print("Теперь можно тестировать генерацию аудио на http://72.56.66.228/module/vacancies")
    else:
        print("\n❌ Проблема с ElevenLabs API")
