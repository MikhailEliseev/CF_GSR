#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import scp
import os
from datetime import datetime

def deploy_html_update():
    """Деплой обновленного HTML на сервер"""
    
    print("🚀 Начинаем деплой HTML обновления...")
    
    # SSH подключение
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("🔐 Подключаемся к серверу...")
        ssh.connect('72.56.66.228', username='root', password='g2D,RytdQoSAYv')
        print("✅ Подключение успешно")
        
        # Шаг 8.1: Создать бекап HTML
        print("📦 Создаем бекап module_vacancies.html...")
        backup_cmd = f"cp /root/templates/module_vacancies.html /root/templates/module_vacancies.html.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        stdout.read()
        print("✅ Бекап HTML создан")
        
        # Шаг 8.2: Загрузить HTML
        print("📤 Загружаем обновленный module_vacancies.html...")
        with scp.SCPClient(ssh.get_transport()) as scp_client:
            scp_client.put('templates/module_vacancies.html', '/root/templates/module_vacancies.html')
        print("✅ HTML загружен")
        
        # Шаг 8.3: Перезапустить сервер
        print("🔄 Перезапускаем сервер...")
        restart_cmd = "pkill -f python.*app && cd /root && nohup python3 app.py > server.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(restart_cmd)
        stdout.read()
        print("✅ Сервер перезапущен")
        
        print("🎉 HTML деплой завершен успешно!")
        print("🌐 Проверьте: http://72.56.66.228/module/vacancies")
        
    except Exception as e:
        print(f"❌ Ошибка деплоя HTML: {e}")
        return False
    finally:
        ssh.close()
    
    return True

if __name__ == '__main__':
    deploy_html_update()
