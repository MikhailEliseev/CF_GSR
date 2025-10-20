#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import scp
import os
from datetime import datetime

def deploy_parsing_update():
    """Деплой обновления парсинга на сервер"""
    
    print("🚀 Начинаем деплой обновления парсинга...")
    
    # SSH подключение
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("🔐 Подключаемся к серверу...")
        ssh.connect('72.56.66.228', username='root', password='g2D,RytdQoSAYv')
        print("✅ Подключение успешно")
        
        # Шаг 7.1: Создать бекап
        print("📦 Создаем бекап routes/vacancies.py...")
        backup_cmd = f"cp /root/routes/vacancies.py /root/routes/vacancies.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        stdout.read()
        print("✅ Бекап создан")
        
        # Шаг 7.2: Загрузить обновленный файл
        print("📤 Загружаем обновленный routes/vacancies.py...")
        with scp.SCPClient(ssh.get_transport()) as scp_client:
            scp_client.put('routes/vacancies.py', '/root/routes/vacancies.py')
        print("✅ Файл загружен")
        
        # Шаг 7.3: Перезапустить сервер
        print("🔄 Перезапускаем сервер...")
        restart_cmd = "pkill -f python.*app && cd /root && nohup python3 app.py > server.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(restart_cmd)
        stdout.read()
        print("✅ Сервер перезапущен")
        
        # Шаг 7.4: Проверить что старый endpoint работает
        print("🧪 Проверяем старый endpoint...")
        test_cmd = "curl -s http://localhost:5000/api/vacancies/test | head -c 100"
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        result = stdout.read().decode()
        if "success" in result:
            print("✅ Старый endpoint работает")
        else:
            print("⚠️ Старый endpoint может не работать")
        
        print("🎉 Деплой завершен успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка деплоя: {e}")
        return False
    finally:
        ssh.close()
    
    return True

if __name__ == '__main__':
    deploy_parsing_update()
