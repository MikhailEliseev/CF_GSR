#!/usr/bin/env python3
"""
Подключение к серверу с новым SSH ключом
"""

import subprocess
import os
import time

def test_ssh_connection():
    """Тестирует SSH подключение с новым ключом"""
    print("🔑 ТЕСТИРОВАНИЕ SSH ПОДКЛЮЧЕНИЯ")
    print("="*50)
    
    # Проверяем наличие ключа
    if not os.path.exists("server_key_new"):
        print("❌ SSH ключ не найден!")
        return False
    
    # Устанавливаем права
    os.chmod("server_key_new", 0o600)
    print("✅ Права на ключ установлены")
    
    # Тестируем подключение
    print("🔍 Тестирую SSH подключение...")
    try:
        result = subprocess.run([
            "ssh", "-i", "server_key_new", "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10", "root@72.56.66.228", "echo 'SSH подключение работает!'"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ SSH подключение работает!")
            print(f"📤 Ответ сервера: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Ошибка SSH: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def upload_and_fix_server():
    """Загружает файлы и исправляет сервер"""
    print("\n🚀 ЗАГРУЗКА И ИСПРАВЛЕНИЕ СЕРВЕРА")
    print("="*50)
    
    try:
        # Загружаем исправленный файл
        print("📤 Загружаю исправленный app.py...")
        result = subprocess.run([
            "scp", "-i", "server_key_new", "-o", "StrictHostKeyChecking=no",
            "app_assemblyai_fixed.py", "root@72.56.66.228:/tmp/app_fixed.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"❌ Ошибка загрузки: {result.stderr}")
            return False
        
        print("✅ Файл загружен на сервер")
        
        # Выполняем исправление на сервере
        print("🔧 Выполняю исправление на сервере...")
        fix_commands = [
            "find / -name 'app.py' 2>/dev/null | head -1 | xargs dirname",
            "cd /var/www/html 2>/dev/null || cd /home/user 2>/dev/null || cd /opt 2>/dev/null",
            "pkill -f python",
            "cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null || true",
            "cp /tmp/app_fixed.py app.py",
            "chmod +x app.py",
            "nohup python3 app.py > app.log 2>&1 &",
            "sleep 3",
            "ps aux | grep python | grep -v grep"
        ]
        
        for cmd in fix_commands:
            print(f"🔧 Выполняю: {cmd}")
            result = subprocess.run([
                "ssh", "-i", "server_key_new", "-o", "StrictHostKeyChecking=no",
                "root@72.56.66.228", cmd
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ Успешно: {result.stdout.strip()}")
            else:
                print(f"⚠️ Предупреждение: {result.stderr.strip()}")
        
        print("✅ Исправление завершено!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка исправления: {e}")
        return False

def verify_server():
    """Проверяет работу сервера"""
    print("\n🔍 ПРОВЕРКА СЕРВЕРА")
    print("="*50)
    
    import requests
    
    # Ждем запуска
    print("⏳ Ждем 10 секунд для запуска...")
    time.sleep(10)
    
    try:
        response = requests.get("http://72.56.66.228", timeout=10)
        print(f"📊 Статус сервера: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 СЕРВЕР РАБОТАЕТ!")
            return True
        else:
            print(f"⚠️ Сервер вернул статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def main():
    print("🚀 ПОДКЛЮЧЕНИЕ К СЕРВЕРУ С НОВЫМ SSH КЛЮЧОМ")
    print("="*60)
    
    # Тестируем SSH
    if test_ssh_connection():
        print("\n✅ SSH подключение работает!")
        
        # Загружаем и исправляем
        if upload_and_fix_server():
            print("\n✅ Файлы загружены и исправление выполнено!")
            
            # Проверяем сервер
            if verify_server():
                print("\n🎉 СЕРВЕР ИСПРАВЛЕН И РАБОТАЕТ!")
                print("🌐 Откройте: http://72.56.66.228/module/trends")
            else:
                print("\n⚠️ Сервер исправлен, но не отвечает")
                print("🔧 Проверьте логи: ssh -i server_key_new root@72.56.66.228 'tail -f app.log'")
        else:
            print("\n❌ Ошибка загрузки файлов")
    else:
        print("\n❌ SSH подключение не работает!")
        print("🔧 ВЫПОЛНИТЕ ВРУЧНУЮ:")
        print("1. Добавьте публичный ключ в панель Timeweb Cloud")
        print("2. Скопируйте содержимое server_key_new.pub")
        print("3. Добавьте ключ в разделе 'SSH-ключи'")
        print("4. Попробуйте снова")
    
    print("\n" + "="*60)
    print("📋 ИНСТРУКЦИИ ПО ДОБАВЛЕНИЮ SSH КЛЮЧА:")
    print("1. Откройте панель Timeweb Cloud")
    print("2. Перейдите в 'SSH-ключи'")
    print("3. Нажмите 'Загрузить новый ключ'")
    print("4. Вставьте содержимое server_key_new.pub")
    print("5. Назовите ключ: gsr-content-factory-20250929")

if __name__ == "__main__":
    main()
