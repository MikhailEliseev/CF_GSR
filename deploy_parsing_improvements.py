#!/usr/bin/env python3
"""
Скрипт для деплоя улучшений парсинга вакансий на сервер
"""

import paramiko
import scp
import time
import os
from datetime import datetime

# SSH настройки
SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def connect_ssh():
    """Подключение по SSH"""
    print("🔌 Подключаемся к серверу...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    print("✅ Подключение успешно")
    return ssh

def create_backup(ssh):
    """Создание бекапа"""
    print("💾 Создаем бекап...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_cmd = f"cp /root/routes/vacancies.py /root/routes/vacancies.py.backup_{timestamp}"
    
    stdin, stdout, stderr = ssh.exec_command(backup_cmd)
    stdout.read()
    stderr.read()
    
    print(f"✅ Бекап создан: vacancies.py.backup_{timestamp}")
    return timestamp

def deploy_file(ssh):
    """Загрузка обновленного файла"""
    print("📤 Загружаем обновленный routes/vacancies.py...")
    
    with scp.SCPClient(ssh.get_transport()) as scp_client:
        scp_client.put('routes/vacancies.py', '/root/routes/vacancies.py')
        print("✅ Файл загружен")
    
    # Проверяем что файл загрузился
    check_cmd = "ls -la /root/routes/vacancies.py"
    stdin, stdout, stderr = ssh.exec_command(check_cmd)
    result = stdout.read().decode().strip()
    print(f"📁 Файл на сервере: {result}")

def restart_server(ssh):
    """Перезапуск сервера"""
    print("🔄 Перезапускаем сервер...")
    
    # Останавливаем старые процессы
    stop_cmd = "pkill -f python.*app"
    stdin, stdout, stderr = ssh.exec_command(stop_cmd)
    stdout.read()
    stderr.read()
    
    time.sleep(2)
    
    # Запускаем сервер
    start_cmd = "cd /root && nohup python3 app.py > server.log 2>&1 &"
    stdin, stdout, stderr = ssh.exec_command(start_cmd)
    stdout.read()
    stderr.read()
    
    time.sleep(3)
    
    # Проверяем что сервер запустился
    check_cmd = "ps aux | grep python.*app | grep -v grep"
    stdin, stdout, stderr = ssh.exec_command(check_cmd)
    processes = stdout.read().decode().strip()
    
    if processes:
        print("✅ Сервер запущен")
        print(f"📊 Процессы: {processes}")
    else:
        print("❌ Сервер не запустился")
        return False
    
    return True

def test_api(ssh):
    """Тестирование API"""
    print("🧪 Тестируем API...")
    
    # Проверяем что сервер отвечает
    test_cmd = "curl -s http://localhost:5000/api/vacancies/test"
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    result = stdout.read().decode().strip()
    
    if "success" in result:
        print("✅ API работает")
        return True
    else:
        print(f"❌ API не работает: {result}")
        return False

def main():
    """Основная функция"""
    print("🚀 Начинаем деплой улучшений парсинга вакансий...")
    
    try:
        # Подключаемся
        ssh = connect_ssh()
        
        # Создаем бекап
        backup_timestamp = create_backup(ssh)
        
        # Загружаем файл
        deploy_file(ssh)
        
        # Перезапускаем сервер
        if not restart_server(ssh):
            print("❌ Не удалось перезапустить сервер")
            return False
        
        # Тестируем API
        if not test_api(ssh):
            print("❌ API не работает после деплоя")
            return False
        
        print("🎉 Деплой завершен успешно!")
        print(f"💾 Бекап: vacancies.py.backup_{backup_timestamp}")
        print("🌐 Сервер: http://72.56.66.228/module/vacancies")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка деплоя: {e}")
        return False
    
    finally:
        if 'ssh' in locals():
            ssh.close()

if __name__ == "__main__":
    main()
