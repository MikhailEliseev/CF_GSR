#!/usr/bin/env python3
"""
Скрипт для деплоя исправления парсинга Google Sheets URL
"""

import paramiko
import scp
import os
import time
from datetime import datetime

# SSH конфигурация
SSH_CONFIG = {
    'hostname': '72.56.66.228',
    'username': 'root',
    'password': 'g2D,RytdQoSAYv',
    'port': 22
}

def connect_ssh():
    """Подключение к серверу по SSH"""
    print("🔌 Подключаемся к серверу...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(**SSH_CONFIG)
        print("✅ SSH подключение установлено")
        return ssh
    except Exception as e:
        print(f"❌ Ошибка SSH подключения: {e}")
        return None

def create_backup(ssh):
    """Создание бэкапа routes/vacancies.py"""
    print("💾 Создаем бэкап routes/vacancies.py...")
    
    try:
        # Ищем проект на сервере
        find_cmd = "find /root -name 'routes' -type d 2>/dev/null | head -3"
        stdin, stdout, stderr = ssh.exec_command(find_cmd)
        routes_dirs = stdout.read().decode().strip().split('\n')
        
        actual_path = None
        for routes_dir in routes_dirs:
            if routes_dir and 'vacancies.py' in str(ssh.exec_command(f"ls {routes_dir} 2>/dev/null")[1].read()):
                actual_path = routes_dir
                break
        
        if not actual_path:
            # Пробуем стандартные пути
            check_dirs = ["/root/routes", "/root/content_factory/routes", "/root/gsr/routes", "/root/app/routes"]
            for dir_path in check_dirs:
                stdin, stdout, stderr = ssh.exec_command(f"ls {dir_path}/vacancies.py 2>/dev/null")
                if not stderr.read():
                    actual_path = dir_path
                    break
        
        if not actual_path:
            print("❌ Не найден файл routes/vacancies.py на сервере")
            return False
        
        print(f"📁 Найден routes в: {actual_path}")
        
        # Создаем бэкап
        backup_cmd = f"cp {actual_path}/vacancies.py {actual_path}/vacancies_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        stdout.read()
        stderr.read()
        print("✅ Бэкап создан")
        
        return actual_path
        
    except Exception as e:
        print(f"❌ Ошибка создания бэкапа: {e}")
        return False

def upload_file(ssh, routes_path):
    """Загрузка исправленного файла на сервер"""
    print("📤 Загружаем исправленный routes/vacancies.py...")
    
    try:
        with scp.SCPClient(ssh.get_transport()) as scp_client:
            scp_client.put('routes/vacancies.py', f"{routes_path}/vacancies.py")
        print("✅ Файл загружен")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки файла: {e}")
        return False

def restart_server(ssh):
    """Перезапуск Flask приложения"""
    print("🔄 Перезапускаем сервер...")
    
    try:
        # Останавливаем существующие процессы
        kill_cmd = "pkill -f 'python.*app' || pkill -f 'flask' || true"
        stdin, stdout, stderr = ssh.exec_command(kill_cmd)
        stdout.read()
        stderr.read()
        time.sleep(2)
        
        # Запускаем сервер в фоне
        start_cmd = "cd /root && nohup python3 app.py > server.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(start_cmd)
        stdout.read()
        stderr.read()
        
        time.sleep(3)
        
        # Проверяем что сервер запустился
        check_cmd = "ps aux | grep -E '(python.*app|flask)' | grep -v grep"
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        processes = stdout.read().decode().strip()
        
        if processes:
            print("✅ Сервер запущен")
            return True
        else:
            print("❌ Сервер не запустился")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка перезапуска сервера: {e}")
        return False

def test_fix():
    """Тестирование исправления"""
    print("🧪 Тестируем исправление...")
    
    import requests
    
    test_url = "https://docs.google.com/spreadsheets/u/1/d/1I1AfpmNbd-K0Osd4Vh7npDCYSQr2a1t_KdT8ms9vgr4/edit?gid=718924971"
    
    try:
        response = requests.post(
            "http://72.56.66.228/api/vacancies/parse",
            json={"url": test_url},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Парсинг Google Sheets работает!")
                print(f"📊 Загружено вакансий: {data.get('count', 0)}")
                return True
            else:
                print(f"❌ Ошибка парсинга: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def main():
    """Основная функция деплоя"""
    print("🚀 Начинаем деплой исправления парсинга Google Sheets...")
    
    # Проверяем что файл существует
    if not os.path.exists('routes/vacancies.py'):
        print("❌ Файл routes/vacancies.py не найден")
        return False
    
    # Подключаемся к серверу
    ssh = connect_ssh()
    if not ssh:
        return False
    
    try:
        # Создаем бэкап
        routes_path = create_backup(ssh)
        if not routes_path:
            return False
        
        # Загружаем исправленный файл
        if not upload_file(ssh, routes_path):
            return False
        
        # Перезапускаем сервер
        if not restart_server(ssh):
            return False
        
        # Тестируем исправление
        if test_fix():
            print("🎉 Деплой успешно завершен!")
            return True
        else:
            print("⚠️ Деплой завершен, но тест не прошел")
            return False
            
    finally:
        ssh.close()
        print("🔌 SSH соединение закрыто")

if __name__ == "__main__":
    main()

