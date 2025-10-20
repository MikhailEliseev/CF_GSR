#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import requests
import json

def update_elevenlabs_key():
    """Обновление ElevenLabs API ключа на сервере"""
    
    print("🚀 Обновляем ElevenLabs API ключ на сервере...")
    
    # SSH подключение
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("🔐 Подключаемся к серверу...")
        ssh.connect('72.56.66.228', username='root', password='g2D,RytdQoSAYv')
        print("✅ Подключение успешно")
        
        # Обновляем ключ через API
        print("🔑 Обновляем ElevenLabs API ключ...")
        
        # Получаем текущие настройки
        get_cmd = "curl -s http://localhost:5000/api/settings/vacancies"
        stdin, stdout, stderr = ssh.exec_command(get_cmd)
        current_settings = stdout.read().decode()
        print(f"📋 Текущие настройки: {current_settings[:200]}...")
        
        # Обновляем ключ
        update_data = {
            "elevenlabs_api_key": "sk_76ff61f01df7d9a12c594e8f45cfa349d1917402ba5ec828"
        }
        
        update_cmd = f"""curl -X POST http://localhost:5000/api/settings/vacancies \
            -H "Content-Type: application/json" \
            -d '{json.dumps(update_data)}'"""
        
        stdin, stdout, stderr = ssh.exec_command(update_cmd)
        result = stdout.read().decode()
        print(f"📤 Результат обновления: {result}")
        
        # Проверяем что ключ обновился
        print("🧪 Проверяем обновленный ключ...")
        check_cmd = "curl -s http://localhost:5000/api/settings/vacancies | grep -o 'sk_[a-zA-Z0-9]*' | head -1"
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        updated_key = stdout.read().decode().strip()
        
        if updated_key:
            print(f"✅ Ключ обновлен: {updated_key[:20]}...")
        else:
            print("⚠️ Не удалось проверить обновление ключа")
        
        print("🎉 Обновление ElevenLabs ключа завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка обновления ключа: {e}")
        return False
    finally:
        ssh.close()
    
    return True

if __name__ == '__main__':
    update_elevenlabs_key()
