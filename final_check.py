#!/usr/bin/env python3
"""
Финальная проверка сервера после обновления
"""

import requests
import time
import json

def check_server_final():
    """Финальная проверка сервера"""
    print("🔍 ФИНАЛЬНАЯ ПРОВЕРКА СЕРВЕРА")
    print("="*50)
    
    # Проверяем базовую доступность
    print("📡 Проверяем базовую доступность...")
    try:
        response = requests.get("http://72.56.66.228", timeout=10)
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Сервер работает!")
            return True
        elif response.status_code == 502:
            print("❌ 502 Bad Gateway - приложение не запущено")
            return False
        else:
            print(f"⚠️ Неожиданный статус: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

def check_demo_data():
    """Проверяем демо данные"""
    print("\n🔍 Проверяем демо данные...")
    
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
                    print("❌ ДЕМО ДАННЫЕ ВСЕ ЕЩЕ ЕСТЬ!")
                    print(f"   Пример: {caption[:100]}...")
                    return True
                else:
                    print("✅ ДЕМО ДАННЫЕ УБРАНЫ!")
                    print(f"   Пример: {caption[:100]}...")
                    return False
            else:
                print("⚠️ API не вернул данных")
                return None
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return None

def show_final_status(server_works, has_demo):
    """Показывает финальный статус"""
    print("\n" + "="*60)
    print("📋 ФИНАЛЬНЫЙ СТАТУС")
    print("="*60)
    
    if server_works is True and has_demo is False:
        print("🎉 ОТЛИЧНО! ПРОБЛЕМА ПОЛНОСТЬЮ РЕШЕНА!")
        print("✅ Сервер работает")
        print("✅ Приложение запущено")
        print("✅ Демо данные убраны")
        print("✅ Система готова к использованию!")
        print("\n🌐 Откройте: http://72.56.66.228/module/trends")
        
    elif server_works is False:
        print("❌ СЕРВЕР НЕ ЗАПУЩЕН!")
        print("🔧 НУЖНО ЗАПУСТИТЬ ПРИЛОЖЕНИЕ:")
        print("1. Подключитесь к серверу: ssh user@72.56.66.228")
        print("2. Найдите папку: find / -name 'app.py'")
        print("3. Перейдите в папку: cd /path/to/app")
        print("4. Запустите: python3 app.py")
        print("\n📁 ИНСТРУКЦИИ:")
        print("✅ SERVER_STARTUP_INSTRUCTIONS.md - Как запустить")
        print("✅ app_for_server_final.py - Файл без демо данных")
        
    elif has_demo is True:
        print("❌ ДЕМО ДАННЫЕ ВСЕ ЕЩЕ ЕСТЬ!")
        print("🔧 НУЖНО ЗАМЕНИТЬ ФАЙЛ app.py:")
        print("1. Загрузите app_for_server_final.py на сервер")
        print("2. Замените app.py на сервере")
        print("3. Перезапустите приложение")
        print("\n📁 ГОТОВЫЕ ФАЙЛЫ:")
        print("✅ app_for_server_final.py - ВЕРСИЯ БЕЗ ДЕМО ДАННЫХ")
        print("✅ SERVER_STARTUP_INSTRUCTIONS.md - Инструкции")
        
    else:
        print("⚠️ НЕ УДАЛОСЬ ПРОВЕРИТЬ ДЕМО ДАННЫЕ")
        print("🔧 Возможно, есть проблемы с API")
        print("📁 Проверьте SERVER_STARTUP_INSTRUCTIONS.md")

def main():
    print("🚀 ФИНАЛЬНАЯ ПРОВЕРКА СЕРВЕРА")
    print("="*60)
    
    # Проверяем сервер
    server_works = check_server_final()
    
    if server_works is True:
        # Проверяем демо данные
        has_demo = check_demo_data()
        
        # Показываем финальный статус
        show_final_status(server_works, has_demo)
        
    else:
        # Сервер не работает
        show_final_status(server_works, None)
    
    print("\n" + "="*60)
    print("📞 ЕСЛИ ВОЗНИКНУТ ПРОБЛЕМЫ:")
    print("1. Проверьте SERVER_STARTUP_INSTRUCTIONS.md")
    print("2. Убедитесь, что файл app.py заменен")
    print("3. Проверьте, что приложение запущено")
    print("4. Проверьте логи: tail -f app.log")
    print("\n🌐 ВЕБ-ИНТЕРФЕЙС: http://localhost:5000")

if __name__ == "__main__":
    main()
