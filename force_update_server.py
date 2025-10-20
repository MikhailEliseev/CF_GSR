#!/usr/bin/env python3
"""
Принудительное обновление сервера - убираем демо данные
"""

import requests
import json
import time

def check_demo_data():
    """Проверяет демо данные на сервере"""
    print("🔍 Проверяем демо данные на сервере...")
    
    try:
        response = requests.post(
            "http://72.56.66.228/api/trends/collect-reels",
            json={"competitors": ["rem.vac"], "count": 3},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('reels'):
                first_reel = data['reels'][0]
                caption = first_reel.get('caption', '')
                
                # Проверяем признаки демо данных
                demo_indicators = ['демо', 'demo', 'пример контента', '21.01.1970']
                has_demo = any(indicator in caption.lower() for indicator in demo_indicators)
                
                if has_demo:
                    print("❌ ПОДТВЕРЖДЕНО: На сервере демо данные!")
                    print(f"   Пример: {caption[:100]}...")
                    return True
                else:
                    print("✅ ОТЛИЧНО: На сервере реальные данные!")
                    return False
            else:
                print("⚠️ Сервер не вернул данных")
                return None
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

def show_manual_update_instructions():
    """Показывает инструкции для ручного обновления"""
    print("\n" + "="*60)
    print("🚨 КРИТИЧЕСКОЕ ОБНОВЛЕНИЕ СЕРВЕРА")
    print("="*60)
    print()
    print("❌ ПРОБЛЕМА: На сервере демо данные!")
    print("🎯 РЕШЕНИЕ: Немедленно обновить сервер")
    print()
    print("🚀 НЕМЕДЛЕННЫЕ ДЕЙСТВИЯ:")
    print("1. Подключитесь к серверу: ssh root@72.56.66.228")
    print("2. Найдите папку с приложением")
    print("3. Сделайте резервную копию: cp app.py app_backup.py")
    print("4. Замените app.py на app_for_server_final.py")
    print("5. Перезапустите: pkill -f python && python3 app.py")
    print()
    print("📁 ФАЙЛЫ ДЛЯ ОБНОВЛЕНИЯ:")
    print("✅ app_for_server_final.py - ВЕРСИЯ БЕЗ ДЕМО ДАННЫХ")
    print("✅ URGENT_SERVER_UPDATE.md - Срочная инструкция")
    print("✅ verify_server_fix.py - Проверка после обновления")
    print()
    print("🔍 СПОСОБЫ ЗАГРУЗКИ ФАЙЛА:")
    print("1. SCP: scp app_for_server_final.py root@72.56.66.228:/path/to/app.py")
    print("2. FTP/SFTP: Загрузите через FTP клиент")
    print("3. Веб-панель: Загрузите через файловый менеджер хостинга")
    print("4. Git: git push (если используется Git)")
    print()
    print("⚠️ КРИТИЧНО:")
    print("- ДЕМО ДАННЫЕ В ПРОДАКШЕНЕ НЕДОПУСТИМЫ!")
    print("- Обновите сервер немедленно!")
    print("- Проверьте результат после обновления")

def create_emergency_script():
    """Создает экстренный скрипт для обновления"""
    script_content = """#!/bin/bash
# ЭКСТРЕННОЕ ОБНОВЛЕНИЕ СЕРВЕРА - УБИРАЕМ ДЕМО ДАННЫЕ

echo "🚨 ЭКСТРЕННОЕ ОБНОВЛЕНИЕ СЕРВЕРА"
echo "================================"

# Параметры (измените под ваши)
SERVER="72.56.66.228"
USER="root"
REMOTE_PATH="/root/gsr"  # Измените на ваш путь

echo "📡 Подключение к серверу: $USER@$SERVER"
echo "📁 Путь к приложению: $REMOTE_PATH"

# Проверяем файл
if [ ! -f "app_for_server_final.py" ]; then
    echo "❌ Файл app_for_server_final.py не найден!"
    echo "🔧 Создайте файл с исправленным кодом"
    exit 1
fi

echo "✅ Файл app_for_server_final.py найден"

# Создаем резервную копию
echo "💾 Создаем резервную копию..."
ssh $USER@$SERVER "cd $REMOTE_PATH && cp app.py app_backup_\$(date +%Y%m%d_%H%M%S).py"

# Загружаем исправленный файл
echo "📤 Загружаем исправленный файл..."
scp app_for_server_final.py $USER@$SERVER:$REMOTE_PATH/app.py

# Перезапускаем приложение
echo "🔄 Перезапускаем приложение..."
ssh $USER@$SERVER "cd $REMOTE_PATH && pkill -f python && python3 app.py &"

# Ждем запуска
echo "⏳ Ждем запуска приложения..."
sleep 5

# Проверяем результат
echo "🔍 Проверяем результат..."
python3 verify_server_fix.py

echo ""
echo "🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО!"
echo "======================="
echo "✅ Файл заменен на сервере"
echo "✅ Приложение перезапущено"
echo "✅ Демо данные должны быть убраны"
echo ""
echo "🔍 ПРОВЕРКА:"
echo "1. Откройте http://72.56.66.228/module/trends"
echo "2. Нажмите 'Собрать рилсы конкурентов'"
echo "3. Убедитесь, что нет 'Демо-пост' и дат '21.01.1970'"
"""
    
    with open("emergency_update.sh", "w") as f:
        f.write(script_content)
    
    import os
    os.chmod("emergency_update.sh", 0o755)
    print("✅ Создан экстренный скрипт emergency_update.sh")

def main():
    print("🚨 ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ СЕРВЕРА")
    print("Убираем демо данные из модуля трендов")
    print("="*50)
    
    # Проверяем демо данные
    has_demo = check_demo_data()
    
    if has_demo is True:
        print("\n❌ КРИТИЧЕСКАЯ ПРОБЛЕМА: Демо данные на сервере!")
        print("🎯 НЕМЕДЛЕННОЕ ОБНОВЛЕНИЕ ТРЕБУЕТСЯ!")
        
        # Показываем инструкции
        show_manual_update_instructions()
        
        # Создаем экстренный скрипт
        create_emergency_script()
        
        print("\n" + "="*60)
        print("🚀 ГОТОВЫЕ ИНСТРУМЕНТЫ:")
        print("✅ emergency_update.sh - Экстренный скрипт обновления")
        print("✅ app_for_server_final.py - Файл без демо данных")
        print("✅ verify_server_fix.py - Проверка после обновления")
        print("✅ URGENT_SERVER_UPDATE.md - Срочная инструкция")
        print()
        print("🎯 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Запустите: ./emergency_update.sh")
        print("2. Или следуйте инструкциям в URGENT_SERVER_UPDATE.md")
        print("3. Проверьте результат")
        
    elif has_demo is False:
        print("\n✅ ОТЛИЧНО: На сервере уже реальные данные!")
        print("🎉 Обновление не требуется")
        
    else:
        print("\n⚠️ НЕ УДАЛОСЬ ПРОВЕРИТЬ СЕРВЕР")
        print("🔧 Возможно, сервер недоступен или есть проблемы с API")
        show_manual_update_instructions()

if __name__ == "__main__":
    main()
