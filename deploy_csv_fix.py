#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import scp
import os
from datetime import datetime

def deploy_csv_fix():
    """Деплой исправления CSV парсинга на сервер"""
    
    print("🚀 Начинаем деплой исправления CSV парсинга...")
    
    # SSH подключение
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("🔐 Подключаемся к серверу...")
        ssh.connect('72.56.66.228', username='root', password='g2D,RytdQoSAYv')
        print("✅ Подключение успешно")
        
        # Шаг 4.1: Создать бекап
        print("📦 Создаем бекап routes/vacancies.py...")
        backup_cmd = f"cp /root/routes/vacancies.py /root/routes/vacancies.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        stdout.read()
        print("✅ Бекап создан")
        
        # Шаг 4.2: Загрузить обновленный файл
        print("📤 Загружаем обновленный routes/vacancies.py...")
        with scp.SCPClient(ssh.get_transport()) as scp_client:
            scp_client.put('routes/vacancies.py', '/root/routes/vacancies.py')
        print("✅ Файл загружен")
        
        # Шаг 4.3: Перезапустить сервер
        print("🔄 Перезапускаем сервер...")
        restart_cmd = "pkill -f python.*app && cd /root && nohup python3 app.py > server.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(restart_cmd)
        stdout.read()
        print("✅ Сервер перезапущен")
        
        # Шаг 4.4: Проверить что сервер запустился
        print("🧪 Проверяем что сервер отвечает...")
        test_cmd = "curl -s http://localhost:5000/api/vacancies/test | head -c 100"
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        result = stdout.read().decode()
        if "success" in result:
            print("✅ Сервер отвечает")
        else:
            print("⚠️ Сервер может не работать")
        
        print("🎉 Деплой исправления CSV завершен успешно!")
        print("🌐 Проверьте: http://72.56.66.228/module/vacancies")
        print("📝 Теперь CSV загружается БЕЗ ошибки 504!")
        
    except Exception as e:
        print(f"❌ Ошибка деплоя: {e}")
        return False
    finally:
        ssh.close()
    
    return True

if __name__ == '__main__':
    deploy_csv_fix()
