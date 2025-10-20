#!/usr/bin/env python3
"""
Скрипт для деплоя обновленного module_vacancies.html на сервер
"""

import paramiko
import scp
import time
from datetime import datetime

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def main():
    print("🚀 Деплой module_vacancies.html на сервер...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
        print("✅ Подключились к серверу")
        
        # Бекап
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_cmd = f"cp /root/templates/module_vacancies.html /root/templates/module_vacancies.html.backup_{timestamp}"
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        stdout.read()
        print(f"💾 Создан бекап: module_vacancies.html.backup_{timestamp}")
        
        # Загрузка
        with scp.SCPClient(ssh.get_transport()) as scp_client:
            scp_client.put('templates/module_vacancies.html', '/root/templates/module_vacancies.html')
        print("📤 HTML файл загружен")
        
        # Проверка
        check_cmd = "grep -c 'Загрузить CSV' /root/templates/module_vacancies.html"
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        count = stdout.read().decode().strip()
        print(f"🔍 Проверка: найдено '{count}' вхождений 'Загрузить CSV'")
        
        # Перезапуск
        ssh.exec_command("pkill -f python.*app")
        time.sleep(2)
        ssh.exec_command("cd /root && nohup python3 app.py > server.log 2>&1 &")
        time.sleep(3)
        print("🔄 Сервер перезапущен")
        
        # Проверка процесса
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep python.*app | grep -v grep")
        processes = stdout.read().decode().strip()
        if processes:
            print("✅ Сервер работает")
        else:
            print("❌ Сервер не запустился!")
        
        ssh.close()
        print("🎉 Деплой завершен! Обновите страницу: http://72.56.66.228/module/vacancies")
        
    except Exception as e:
        print(f"❌ Ошибка деплоя: {e}")

if __name__ == "__main__":
    main()