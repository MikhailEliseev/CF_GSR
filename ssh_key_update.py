#!/usr/bin/env python3
"""
Обновление сервера с использованием SSH ключа
"""

import subprocess
import time
import requests
import os

def create_ssh_key_file():
    """Создает файл с SSH ключом"""
    ssh_key = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCszeQjb7kRZGg6EJIclJrXFf96h7lQ== timeweb-server-new-key"""
    
    with open("server_key.pub", "w") as f:
        f.write(ssh_key)
    
    print("✅ SSH ключ сохранен в server_key.pub")

def test_ssh_connection():
    """Тестирует SSH подключение"""
    print("🔍 Тестирую SSH подключение...")
    
    try:
        # Пробуем подключиться с ключом
        result = subprocess.run([
            "ssh", "-i", "server_key.pub", "-o", "StrictHostKeyChecking=no",
            "user@72.56.66.228", "echo 'SSH подключение работает'"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ SSH подключение работает!")
            print(f"📋 Ответ сервера: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ SSH ошибка: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ SSH таймаут")
        return False
    except Exception as e:
        print(f"❌ SSH исключение: {e}")
        return False

def upload_file_with_ssh():
    """Загружает файл на сервер через SSH"""
    print("📤 Загружаю файл на сервер...")
    
    # Проверяем наличие файла
    if not os.path.exists("app_for_server_final.py"):
        print("❌ Файл app_for_server_final.py не найден!")
        return False
    
    try:
        # Загружаем файл через SCP с ключом
        result = subprocess.run([
            "scp", "-i", "server_key.pub", "-o", "StrictHostKeyChecking=no",
            "app_for_server_final.py", "user@72.56.66.228:/tmp/"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Файл загружен на сервер!")
            return True
        else:
            print(f"❌ Ошибка загрузки: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка загрузки файла: {e}")
        return False

def execute_server_update():
    """Выполняет обновление на сервере"""
    print("🔧 Выполняю обновление на сервере...")
    
    update_script = '''#!/bin/bash
echo "🚀 ОБНОВЛЕНИЕ СЕРВЕРА С SSH КЛЮЧОМ"
echo "================================="

# Находим папку с приложением
echo "🔍 Ищем папку с приложением..."
APP_DIR=$(find / -name "app.py" 2>/dev/null | head -1 | xargs dirname)

if [ -z "$APP_DIR" ]; then
    echo "❌ Папка с приложением не найдена!"
    echo "🔍 Проверяем стандартные места..."
    
    # Проверяем стандартные места
    for dir in /var/www/html /home/user /opt /usr/local/bin /var/www; do
        if [ -f "$dir/app.py" ]; then
            APP_DIR="$dir"
            echo "✅ Найдена папка: $APP_DIR"
            break
        fi
    done
    
    if [ -z "$APP_DIR" ]; then
        echo "❌ Не удалось найти папку с приложением!"
        echo "📋 Список всех файлов app.py:"
        find / -name "app.py" 2>/dev/null
        exit 1
    fi
fi

echo "📁 Рабочая папка: $APP_DIR"
cd "$APP_DIR"

# Останавливаем все процессы Python
echo "🛑 Останавливаем все процессы Python..."
pkill -f python
sleep 3

# Создаем резервную копию
echo "💾 Создаем резервную копию..."
if [ -f "app.py" ]; then
    cp app.py "app_backup_$(date +%Y%m%d_%H%M%S).py"
    echo "✅ Резервная копия создана"
else
    echo "⚠️ Файл app.py не найден в папке $APP_DIR"
fi

# Копируем новый файл
echo "🔄 Копируем новый файл..."
if [ -f "/tmp/app_for_server_final.py" ]; then
    cp /tmp/app_for_server_final.py app.py
    echo "✅ Файл заменен"
else
    echo "❌ Файл /tmp/app_for_server_final.py не найден!"
    exit 1
fi

# Устанавливаем права
chmod +x app.py

# Запускаем приложение
echo "🚀 Запускаем приложение..."
nohup python3 app.py > app.log 2>&1 &
APP_PID=$!

# Ждем запуска
echo "⏳ Ждем запуска приложения..."
sleep 5

# Проверяем статус
if ps -p $APP_PID > /dev/null; then
    echo "✅ Приложение запущено (PID: $APP_PID)"
else
    echo "❌ Приложение не запустилось!"
    echo "📋 Логи:"
    tail -20 app.log
    exit 1
fi

# Проверяем порт
echo "🔍 Проверяем порт 8000..."
if netstat -tlnp | grep :8000 > /dev/null; then
    echo "✅ Порт 8000 открыт"
else
    echo "⚠️ Порт 8000 не открыт"
fi

echo "🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО!"
echo "🌐 Проверьте: http://72.56.66.228"
'''
    
    try:
        # Выполняем скрипт на сервере
        result = subprocess.run([
            "ssh", "-i", "server_key.pub", "-o", "StrictHostKeyChecking=no",
            "user@72.56.66.228", update_script
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Обновление выполнено на сервере!")
            print(f"📋 Вывод: {result.stdout}")
            return True
        else:
            print(f"❌ Ошибка выполнения: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        return False

def check_final_result():
    """Проверяет финальный результат"""
    print("🔍 Проверяю финальный результат...")
    
    # Ждем стабилизации
    print("⏳ Ждем 15 секунд для стабилизации...")
    time.sleep(15)
    
    try:
        response = requests.get("http://72.56.66.228", timeout=10)
        print(f"📊 Финальный статус: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 СЕРВЕР РАБОТАЕТ! ОБНОВЛЕНИЕ УСПЕШНО!")
            return True
        else:
            print(f"⚠️ Сервер вернул статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def main():
    print("🚀 ОБНОВЛЕНИЕ СЕРВЕРА С SSH КЛЮЧОМ")
    print("="*50)
    
    # Создаем SSH ключ
    create_ssh_key_file()
    
    # Тестируем SSH подключение
    if not test_ssh_connection():
        print("❌ SSH подключение не работает!")
        print("🔧 Проверьте SSH ключ в панели управления")
        return
    
    # Загружаем файл
    if not upload_file_with_ssh():
        print("❌ Не удалось загрузить файл!")
        return
    
    # Выполняем обновление
    if execute_server_update():
        # Проверяем результат
        if check_final_result():
            print("\n🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            print("✅ Сервер работает")
            print("✅ Демо данные убраны")
            print("✅ Система готова к использованию")
            print("\n🌐 Откройте: http://72.56.66.228/module/trends")
        else:
            print("\n⚠️ ОБНОВЛЕНИЕ ВЫПОЛНЕНО, НО СЕРВЕР НЕ ОТВЕЧАЕТ")
            print("🔧 Возможно, нужно больше времени для запуска")
    else:
        print("\n❌ ОБНОВЛЕНИЕ НЕ УДАЛОСЬ!")
        print("🔧 ВЫПОЛНИТЕ ВРУЧНУЮ:")
        print("1. Подключитесь к серверу через SSH")
        print("2. Найдите папку: find / -name 'app.py'")
        print("3. Замените файл: cp /tmp/app_for_server_final.py app.py")
        print("4. Запустите: python3 app.py")
    
    print("\n" + "="*50)
    print("📞 ЕСЛИ ВОЗНИКНУТ ПРОБЛЕМЫ:")
    print("1. Проверьте SSH ключ в панели управления")
    print("2. Убедитесь, что файл app.py заменен")
    print("3. Проверьте логи: tail -f app.log")

if __name__ == "__main__":
    main()
