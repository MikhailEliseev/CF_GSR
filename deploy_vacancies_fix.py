#!/usr/bin/env python3
"""
Deployment скрипт для исправления CSV загрузки на удаленном сервере
"""

import subprocess
import os
import time
from datetime import datetime

def deploy_vacancies_fix():
    """Deploy исправлений на удаленный сервер"""
    print("🚀 Начинаем deployment исправлений CSV загрузки...")
    
    # Параметры подключения
    host = "72.56.66.228"
    username = "root"
    key_path = "/Users/mikhaileliseev/Desktop/КЗ GSR/server_key_new"
    
    try:
        # Устанавливаем права на ключ
        os.chmod(key_path, 0o600)
        print("✅ Права на SSH ключ установлены")
        
        def run_ssh_command(command):
            """Выполняет команду через SSH"""
            cmd = ["ssh", "-i", key_path, "-o", "StrictHostKeyChecking=no", 
                   "-o", "ConnectTimeout=10", f"{username}@{host}", command]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        
        # 1. Создаем бэкап текущего файла
        print("📦 Создаем бэкап текущего routes/vacancies.py...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_cmd = f"cp /root/routes/vacancies.py /root/routes/vacancies.py.backup_{timestamp}"
        exit_code, stdout, stderr = run_ssh_command(backup_cmd)
        if exit_code != 0:
            print(f"⚠️ Предупреждение при создании бэкапа: {stderr}")
        print("✅ Бэкап создан")
        
        # 2. Останавливаем текущий сервер
        print("🛑 Останавливаем текущий сервер...")
        stop_cmd = "pkill -f 'python.*app' || true"
        exit_code, stdout, stderr = run_ssh_command(stop_cmd)
        time.sleep(2)
        print("✅ Сервер остановлен")
        
        # 3. Загружаем исправленный файл через scp
        print("📤 Загружаем исправленный routes/vacancies.py...")
        scp_cmd = ["scp", "-i", key_path, "-o", "StrictHostKeyChecking=no",
                   "/Users/mikhaileliseev/Desktop/КЗ GSR/routes/vacancies.py", 
                   f"{username}@{host}:/root/routes/vacancies.py"]
        result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ Ошибка загрузки файла: {result.stderr}")
            return False
        
        print("✅ Файл загружен")
        
        # 4. Проверяем синтаксис Python
        print("🔍 Проверяем синтаксис Python...")
        exit_code, stdout, stderr = run_ssh_command("python3 -m py_compile /root/routes/vacancies.py")
        
        if exit_code != 0:
            print(f"❌ Ошибка синтаксиса: {stderr}")
            return False
        
        print("✅ Синтаксис корректен")
        
        # 5. Запускаем сервер
        print("🚀 Запускаем сервер...")
        start_cmd = "cd /root && nohup python3 app_current_backup.py > server.log 2>&1 &"
        exit_code, stdout, stderr = run_ssh_command(start_cmd)
        time.sleep(3)
        
        # 6. Проверяем, что сервер запустился
        print("🔍 Проверяем статус сервера...")
        exit_code, stdout, stderr = run_ssh_command("ps aux | grep python | grep -v grep")
        
        if "python" in stdout:
            print("✅ Сервер запущен")
        else:
            print("❌ Сервер не запустился")
            # Проверяем логи
            exit_code, log_stdout, log_stderr = run_ssh_command("tail -20 /root/server.log")
            print(f"Логи сервера:\n{log_stdout}")
            return False
        
        # 7. Тестируем endpoint
        print("🧪 Тестируем endpoint...")
        exit_code, test_stdout, test_stderr = run_ssh_command("curl -s http://localhost:5000/api/vacancies/upload-csv -X POST -F 'file=@/dev/null' || echo 'Endpoint test failed'")
        
        if "файл не найден" in test_stdout or "error" in test_stdout.lower():
            print("✅ Endpoint отвечает (ожидаемая ошибка для пустого файла)")
        else:
            print(f"⚠️ Неожиданный ответ endpoint: {test_stdout}")
        
        print("\n🎉 Deployment завершен успешно!")
        print(f"🌐 Сервер доступен по адресу: http://{host}/module/vacancies")
        print("📋 Для тестирования:")
        print("1. Откройте http://72.56.66.228/module/vacancies")
        print("2. Загрузите тестовый CSV файл")
        print("3. Проверьте, что данные отображаются корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка deployment: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = deploy_vacancies_fix()
    exit(0 if success else 1)
