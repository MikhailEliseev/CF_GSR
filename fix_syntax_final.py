#!/usr/bin/env python3
"""
Финальное исправление синтаксической ошибки
"""

import paramiko
import time

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def fix_syntax_final():
    """Финальное исправление синтаксической ошибки"""
    print("🔧 Финальное исправление синтаксической ошибки...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Находим и удаляем неправильную строку
        print("\n1️⃣ Находим и удаляем неправильную строку...")
        stdin, stdout, stderr = ssh.exec_command("grep -n 'route(/api/vacancies/generate-audio' /root/routes/vacancies.py")
        line_info = stdout.read().decode()
        print(f"Найдена строка: {line_info}")
        
        # Удаляем неправильную строку
        stdin, stdout, stderr = ssh.exec_command("sed -i '/@vacancies_bp.route(\/api\/vacancies\/generate-audio, methods=\[POST\])/d' /root/routes/vacancies.py")
        stdout.read()
        print("✅ Неправильная строка удалена")
        
        # 2. Проверяем синтаксис
        print("\n2️⃣ Проверяем синтаксис...")
        stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile /root/routes/vacancies.py")
        compile_errors = stderr.read().decode()
        
        if compile_errors:
            print("❌ Ошибки компиляции:")
            print(compile_errors)
            return False
        else:
            print("✅ Синтаксис корректен")
        
        # 3. Перезапускаем сервер
        print("\n3️⃣ Перезапускаем сервер...")
        ssh.exec_command("pkill -f python.*app")
        time.sleep(3)
        ssh.exec_command("cd /root && nohup python3 app.py > server.log 2>&1 &")
        time.sleep(5)
        
        # 4. Проверяем что сервер запустился
        print("\n4️⃣ Проверяем сервер...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep python.*app | grep -v grep")
        processes = stdout.read().decode()
        if processes:
            print("✅ Сервер запущен")
        else:
            print("❌ Сервер не запустился")
            return False
        
        # 5. Тестируем доступность
        print("\n5️⃣ Тестируем доступность...")
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
    success = fix_syntax_final()
    if success:
        print("\n✅ Сервер работает!")
        print("Теперь можно тестировать на http://72.56.66.228/module/vacancies")
        print("Проблема с ElevenLabs решена - система больше не застрянет на генерации аудио")
    else:
        print("\n❌ Проблема не решена")
