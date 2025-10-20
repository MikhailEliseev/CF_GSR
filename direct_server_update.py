#!/usr/bin/env python3
"""
Прямое обновление сервера через SSH
"""

import subprocess
import time
import requests
import os

def run_ssh_command(command, description=""):
    """Выполняет команду на сервере через SSH"""
    print(f"🔧 {description}")
    try:
        # Формируем полную команду SSH
        full_command = f'ssh user@72.56.66.228 "{command}"'
        
        result = subprocess.run(
            full_command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - УСПЕШНО")
            if result.stdout.strip():
                print(f"📋 Вывод: {result.stdout.strip()}")
            return True, result.stdout
        else:
            print(f"❌ {description} - ОШИБКА: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - ТАЙМАУТ")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ {description} - ИСКЛЮЧЕНИЕ: {e}")
        return False, str(e)

def upload_file_to_server():
    """Загружает файл на сервер"""
    print("📤 Загружаем файл на сервер...")
    
    # Проверяем наличие файла
    if not os.path.exists("app_for_server_final.py"):
        print("❌ Файл app_for_server_final.py не найден!")
        return False
    
    try:
        # Загружаем файл на сервер
        result = subprocess.run([
            "scp", 
            "app_for_server_final.py", 
            "user@72.56.66.228:/tmp/"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Файл загружен на сервер")
            return True
        else:
            print(f"❌ Ошибка загрузки: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка загрузки файла: {e}")
        return False

def main():
    print("🚀 ПРЯМОЕ ОБНОВЛЕНИЕ СЕРВЕРА")
    print("="*50)
    
    # Проверяем текущий статус
    print("🔍 Проверяем текущий статус сервера...")
    try:
        response = requests.get("http://72.56.66.228", timeout=10)
        print(f"📊 Статус: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
    
    # Загружаем файл на сервер
    if not upload_file_to_server():
        print("❌ Не удалось загрузить файл на сервер")
        return
    
    # Выполняем команды на сервере
    commands = [
        ("find / -name 'app.py' 2>/dev/null | head -1", "Поиск папки с приложением"),
        ("cd /tmp && ls -la app_for_server_final.py", "Проверка загруженного файла"),
        ("pkill -f python", "Остановка приложения"),
        ("sleep 2", "Ожидание остановки"),
        ("find / -name 'app.py' 2>/dev/null | head -1 | xargs dirname", "Получение пути к папке"),
    ]
    
    app_dir = None
    for command, description in commands:
        success, output = run_ssh_command(command, description)
        if not success:
            print(f"⚠️ Команда не выполнена: {description}")
            continue
            
        # Если это команда получения пути к папке
        if "dirname" in command and success:
            app_dir = output.strip()
            print(f"📁 Найдена папка приложения: {app_dir}")
            break
    
    if not app_dir:
        print("❌ Не удалось найти папку с приложением")
        print("🔧 РУЧНЫЕ ИНСТРУКЦИИ:")
        print("1. Подключитесь к серверу: ssh user@72.56.66.228")
        print("2. Найдите папку: find / -name 'app.py'")
        print("3. Перейдите в папку: cd /path/to/app")
        print("4. Замените файл: cp /tmp/app_for_server_final.py app.py")
        print("5. Запустите: python3 app.py")
        return
    
    # Выполняем обновление
    update_commands = [
        (f"cd {app_dir}", "Переход в папку приложения"),
        (f"cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py", "Создание резервной копии"),
        (f"cp /tmp/app_for_server_final.py app.py", "Замена файла"),
        (f"cd {app_dir} && nohup python3 app.py > app.log 2>&1 &", "Запуск приложения"),
        ("sleep 5", "Ожидание запуска"),
        ("pgrep -f 'python3 app.py'", "Проверка запуска"),
    ]
    
    for command, description in update_commands:
        success, output = run_ssh_command(command, description)
        if not success:
            print(f"⚠️ Команда не выполнена: {description}")
    
    # Проверяем результат
    print("\n🔍 ПРОВЕРКА РЕЗУЛЬТАТА...")
    time.sleep(10)
    
    try:
        response = requests.get("http://72.56.66.228", timeout=10)
        print(f"📊 Финальный статус: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 СЕРВЕР РАБОТАЕТ! ОБНОВЛЕНИЕ УСПЕШНО!")
        else:
            print(f"⚠️ Сервер вернул статус: {response.status_code}")
            print("🔧 Возможно, нужно больше времени для запуска")
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
    
    print("\n" + "="*50)
    print("📞 ПРОВЕРКА РЕЗУЛЬТАТА:")
    print("1. Откройте http://72.56.66.228/module/trends")
    print("2. Нажмите 'Собрать рилсы конкурентов'")
    print("3. Убедитесь, что НЕТ демо данных")

if __name__ == "__main__":
    main()
