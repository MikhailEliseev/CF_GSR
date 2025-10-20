#!/usr/bin/env python3
"""
Проверка статуса сервера
"""

import paramiko
import time

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def check_server():
    """Проверяем статус сервера"""
    print("🔍 Проверяем статус сервера...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Проверяем процессы
        print("\n1️⃣ Проверяем процессы...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep python | grep -v grep")
        processes = stdout.read().decode()
        print("Python процессы:")
        print(processes)
        
        # 2. Проверяем логи
        print("\n2️⃣ Проверяем логи...")
        stdin, stdout, stderr = ssh.exec_command("tail -20 /root/server.log")
        logs = stdout.read().decode()
        print("Последние логи:")
        print(logs)
        
        # 3. Проверяем ошибки в routes/vacancies.py
        print("\n3️⃣ Проверяем синтаксис routes/vacancies.py...")
        stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile /root/routes/vacancies.py")
        compile_result = stdout.read().decode()
        compile_errors = stderr.read().decode()
        
        if compile_errors:
            print("❌ Ошибки компиляции:")
            print(compile_errors)
        else:
            print("✅ Синтаксис routes/vacancies.py корректен")
        
        # 4. Пробуем запустить сервер вручную
        print("\n4️⃣ Пробуем запустить сервер...")
        ssh.exec_command("pkill -f python.*app")
        time.sleep(2)
        
        # Запускаем сервер
        stdin, stdout, stderr = ssh.exec_command("cd /root && python3 app.py > server.log 2>&1 &")
        time.sleep(5)
        
        # Проверяем что запустился
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep python.*app | grep -v grep")
        processes = stdout.read().decode()
        if processes:
            print("✅ Сервер запущен")
        else:
            print("❌ Сервер не запустился")
            
            # Проверяем логи ошибок
            stdin, stdout, stderr = ssh.exec_command("tail -10 /root/server.log")
            error_logs = stdout.read().decode()
            print("Логи ошибок:")
            print(error_logs)
        
        # 5. Тестируем доступность
        print("\n5️⃣ Тестируем доступность...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000/")
        curl_result = stdout.read().decode()
        if "html" in curl_result.lower():
            print("✅ Сервер отвечает")
        else:
            print("❌ Сервер не отвечает")
            print(f"Ответ: {curl_result[:200]}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_server()
