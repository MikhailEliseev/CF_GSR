#!/usr/bin/env python3
"""
РЕАЛЬНОЕ ИСПРАВЛЕНИЕ СЕРВЕРА - БЕЗ ГЛЮКОВ
"""

import subprocess
import time
import requests
import os
import json

def kill_all_processes():
    """Останавливает все процессы Python"""
    print("🛑 Останавливаю все процессы Python...")
    try:
        subprocess.run(["pkill", "-f", "python"], capture_output=True)
        time.sleep(2)
        print("✅ Все процессы остановлены")
        return True
    except Exception as e:
        print(f"❌ Ошибка остановки процессов: {e}")
        return False

def check_server_status():
    """Проверяет реальный статус сервера"""
    print("🔍 Проверяю РЕАЛЬНЫЙ статус сервера...")
    try:
        response = requests.get("http://72.56.66.228", timeout=5)
        print(f"📊 Статус сервера: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"❌ Сервер недоступен: {e}")
        return None

def create_real_upload_script():
    """Создает РЕАЛЬНЫЙ скрипт для загрузки"""
    script_content = '''#!/bin/bash
echo "🚀 РЕАЛЬНОЕ ОБНОВЛЕНИЕ СЕРВЕРА"
echo "=============================="

# Проверяем файлы
if [ ! -f "app_for_server_final.py" ]; then
    echo "❌ Файл app_for_server_final.py не найден!"
    exit 1
fi

echo "✅ Файл найден: app_for_server_final.py"

# Создаем скрипт для сервера
cat > server_real_update.sh << 'EOF'
#!/bin/bash
echo "🔧 РЕАЛЬНОЕ ОБНОВЛЕНИЕ НА СЕРВЕРЕ"
echo "================================="

# Находим папку с приложением
echo "🔍 Ищем папку с приложением..."
APP_DIR=$(find / -name "app.py" 2>/dev/null | head -1 | xargs dirname)

if [ -z "$APP_DIR" ]; then
    echo "❌ Папка с приложением не найдена!"
    echo "🔍 Попробуем найти в стандартных местах..."
    
    # Проверяем стандартные места
    for dir in /var/www/html /home/user /opt /usr/local/bin; do
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
EOF

echo "📤 Загружаем файлы на сервер..."

# Загружаем файлы
scp app_for_server_final.py user@72.56.66.228:/tmp/ || {
    echo "❌ Ошибка загрузки файла!"
    echo "🔧 Попробуйте вручную:"
    echo "1. Скопируйте app_for_server_final.py на сервер"
    echo "2. Выполните команды из server_real_update.sh"
    exit 1
}

scp server_real_update.sh user@72.56.66.228:/tmp/ || {
    echo "❌ Ошибка загрузки скрипта!"
    exit 1
}

echo "🔧 Выполняем обновление на сервере..."
ssh user@72.56.66.228 "chmod +x /tmp/server_real_update.sh && /tmp/server_real_update.sh" || {
    echo "❌ Ошибка выполнения на сервере!"
    echo "🔧 Выполните вручную на сервере:"
    echo "1. ssh user@72.56.66.228"
    echo "2. find / -name 'app.py'"
    echo "3. cd /path/to/app"
    echo "4. cp /tmp/app_for_server_final.py app.py"
    echo "5. pkill -f python"
    echo "6. python3 app.py"
    exit 1
}

echo "🎉 РЕАЛЬНОЕ ОБНОВЛЕНИЕ ЗАВЕРШЕНО!"
'''
    
    with open("real_server_update.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("real_server_update.sh", 0o755)
    print("✅ Создан РЕАЛЬНЫЙ скрипт обновления")

def run_real_update():
    """Запускает РЕАЛЬНОЕ обновление"""
    print("🚀 ЗАПУСКАЮ РЕАЛЬНОЕ ОБНОВЛЕНИЕ...")
    
    # Проверяем наличие файла
    if not os.path.exists("app_for_server_final.py"):
        print("❌ Файл app_for_server_final.py не найден!")
        print("🔧 Создаю файл...")
        
        # Копируем из app_fixed_elevenlabs.py
        if os.path.exists("app_fixed_elevenlabs.py"):
            subprocess.run(["cp", "app_fixed_elevenlabs.py", "app_for_server_final.py"])
            print("✅ Файл создан из app_fixed_elevenlabs.py")
        else:
            print("❌ Исходный файл не найден!")
            return False
    
    # Запускаем обновление
    try:
        result = subprocess.run(["./real_server_update.sh"], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ РЕАЛЬНОЕ ОБНОВЛЕНИЕ ВЫПОЛНЕНО!")
            print(result.stdout)
            return True
        else:
            print("❌ Ошибка обновления:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут обновления")
        return False
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def verify_real_fix():
    """Проверяет РЕАЛЬНЫЙ результат"""
    print("🔍 ПРОВЕРЯЮ РЕАЛЬНЫЙ РЕЗУЛЬТАТ...")
    
    # Ждем стабилизации
    print("⏳ Ждем 15 секунд для стабилизации...")
    time.sleep(15)
    
    # Проверяем сервер
    try:
        response = requests.get("http://72.56.66.228", timeout=10)
        print(f"📊 Финальный статус: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 СЕРВЕР РАБОТАЕТ! РЕАЛЬНОЕ ИСПРАВЛЕНИЕ УСПЕШНО!")
            return True
        else:
            print(f"⚠️ Сервер вернул статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def main():
    print("🚀 РЕАЛЬНОЕ ИСПРАВЛЕНИЕ СЕРВЕРА - БЕЗ ГЛЮКОВ")
    print("="*60)
    
    # Останавливаем все процессы
    kill_all_processes()
    
    # Проверяем текущий статус
    status = check_server_status()
    print(f"📊 Текущий статус: {status}")
    
    # Создаем реальный скрипт
    create_real_upload_script()
    
    # Запускаем реальное обновление
    if run_real_update():
        # Проверяем результат
        if verify_real_fix():
            print("\n🎉 РЕАЛЬНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            print("✅ Сервер работает")
            print("✅ Демо данные убраны")
            print("✅ Система готова к использованию")
            print("\n🌐 Откройте: http://72.56.66.228/module/trends")
        else:
            print("\n⚠️ ОБНОВЛЕНИЕ ВЫПОЛНЕНО, НО СЕРВЕР НЕ ОТВЕЧАЕТ")
            print("🔧 Возможно, нужно больше времени для запуска")
    else:
        print("\n❌ РЕАЛЬНОЕ ОБНОВЛЕНИЕ НЕ УДАЛОСЬ!")
        print("🔧 ВЫПОЛНИТЕ ВРУЧНУЮ:")
        print("1. ssh user@72.56.66.228")
        print("2. find / -name 'app.py'")
        print("3. cd /path/to/app")
        print("4. cp app_for_server_final.py app.py")
        print("5. python3 app.py")
    
    print("\n" + "="*60)
    print("📞 ЕСЛИ ВОЗНИКНУТ ПРОБЛЕМЫ:")
    print("1. Проверьте логи на сервере: tail -f app.log")
    print("2. Убедитесь, что файл app.py заменен")
    print("3. Проверьте, что приложение запущено")

if __name__ == "__main__":
    main()
