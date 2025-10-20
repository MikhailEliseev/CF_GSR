#!/usr/bin/env python3
"""
Простое исправление синтаксической ошибки
"""

import paramiko
import time

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def fix_syntax_simple():
    """Простое исправление синтаксической ошибки"""
    print("🔧 Простое исправление синтаксической ошибки...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Создаем бекап
        print("\n1️⃣ Создаем бекап...")
        stdin, stdout, stderr = ssh.exec_command("cp /root/routes/vacancies.py /root/routes/vacancies.py.backup")
        stdout.read()
        print("✅ Бекап создан")
        
        # 2. Удаляем неправильную строку
        print("\n2️⃣ Удаляем неправильную строку...")
        stdin, stdout, stderr = ssh.exec_command("sed -i '/@vacancies_bp.route(\/api\/vacancies\/generate-audio-fallback, methods=\[POST\])/d' /root/routes/vacancies.py")
        stdout.read()
        print("✅ Неправильная строка удалена")
        
        # 3. Проверяем синтаксис
        print("\n3️⃣ Проверяем синтаксис...")
        stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile /root/routes/vacancies.py")
        compile_errors = stderr.read().decode()
        
        if compile_errors:
            print("❌ Ошибки компиляции:")
            print(compile_errors)
            return False
        else:
            print("✅ Синтаксис корректен")
        
        # 4. Перезапускаем сервер
        print("\n4️⃣ Перезапускаем сервер...")
        ssh.exec_command("pkill -f python.*app")
        time.sleep(3)
        ssh.exec_command("cd /root && nohup python3 app.py > server.log 2>&1 &")
        time.sleep(5)
        
        # 5. Проверяем что сервер запустился
        print("\n5️⃣ Проверяем сервер...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep python.*app | grep -v grep")
        processes = stdout.read().decode()
        if processes:
            print("✅ Сервер запущен")
        else:
            print("❌ Сервер не запустился")
            
            # Проверяем логи
            stdin, stdout, stderr = ssh.exec_command("tail -10 /root/server.log")
            error_logs = stdout.read().decode()
            print("Логи ошибок:")
            print(error_logs)
            return False
        
        # 6. Тестируем доступность
        print("\n6️⃣ Тестируем доступность...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000/")
        curl_result = stdout.read().decode()
        if "html" in curl_result.lower():
            print("✅ Сервер отвечает")
            print("🎉 Проблема решена!")
            return True
        else:
            print("❌ Сервер не отвечает")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    success = fix_syntax_simple()
    if success:
        print("\n✅ Сервер работает!")
        print("Теперь можно тестировать на http://72.56.66.228/module/vacancies")
    else:
        print("\n❌ Проблема не решена")
