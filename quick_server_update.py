#!/usr/bin/env python3
"""
Быстрое обновление сервера - убираем демо данные
"""

import requests
import json
import time

def test_server_demo_data():
    """Проверяет, есть ли демо данные на сервере"""
    print("🔍 Проверяем демо данные на сервере...")
    
    try:
        # Тестируем сбор рилсов
        response = requests.post(
            "http://72.56.66.228/api/trends/collect-reels",
            json={
                "competitors": ["rem.vac"],
                "count": 3
            },
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                reels = data.get('reels', [])
                if reels:
                    first_reel = reels[0]
                    caption = first_reel.get('caption', '')
                    
                    # Проверяем признаки демо данных
                    demo_indicators = [
                        'демо', 'demo', 'ДЕМО', 'DEMO',
                        'пример контента',
                        '21.01.1970',
                        'demo_'
                    ]
                    
                    is_demo = any(indicator in caption.lower() for indicator in demo_indicators)
                    
                    if is_demo:
                        print("❌ НА СЕРВЕРЕ ДЕМО ДАННЫЕ!")
                        print(f"   Пример: {caption[:100]}...")
                        return True
                    else:
                        print("✅ НА СЕРВЕРЕ РЕАЛЬНЫЕ ДАННЫЕ!")
                        print(f"   Пример: {caption[:100]}...")
                        return False
                else:
                    print("⚠️ Сервер не вернул данных")
                    return None
            else:
                print(f"❌ Ошибка сервера: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

def show_update_instructions():
    """Показывает инструкции по обновлению"""
    print("\n" + "="*60)
    print("🔧 ИНСТРУКЦИЯ ПО УБИРАНИЮ ДЕМО ДАННЫХ")
    print("="*60)
    print()
    print("📋 ПРОБЛЕМА: На сервере 72.56.66.228 показываются демо данные")
    print("🎯 РЕШЕНИЕ: Заменить app.py на версию без демо данных")
    print()
    print("🚀 БЫСТРОЕ ОБНОВЛЕНИЕ:")
    print("1. Подключитесь к серверу: ssh user@72.56.66.228")
    print("2. Сделайте резервную копию: cp app.py app_backup.py")
    print("3. Замените содержимое app.py на содержимое app_fixed_elevenlabs.py")
    print("4. Перезапустите: pkill -f python && python3 app.py")
    print()
    print("📁 ФАЙЛЫ ДЛЯ ОБНОВЛЕНИЯ:")
    print("✅ app_fixed_elevenlabs.py - ВЕРСИЯ БЕЗ ДЕМО ДАННЫХ")
    print("✅ API_SETUP_GUIDE.md - Руководство по настройке")
    print("✅ test_api_endpoints.py - Тест endpoints")
    print()
    print("🔍 ПРОВЕРКА ПОСЛЕ ОБНОВЛЕНИЯ:")
    print("1. Откройте http://72.56.66.228/module/trends")
    print("2. Нажмите 'Собрать рилсы конкурентов'")
    print("3. Убедитесь, что нет 'Демо-пост' и дат '21.01.1970'")
    print()
    print("⚠️ ВАЖНО:")
    print("- Сделайте резервную копию перед заменой")
    print("- Проверьте, что Apify API ключ настроен")
    print("- Протестируйте все функции после обновления")

def main():
    print("🚀 ПРОВЕРКА ДЕМО ДАННЫХ НА СЕРВЕРЕ")
    print("="*50)
    
    # Проверяем демо данные
    has_demo = test_server_demo_data()
    
    if has_demo is True:
        print("\n❌ ПОДТВЕРЖДЕНО: На сервере демо данные!")
        show_update_instructions()
    elif has_demo is False:
        print("\n✅ ОТЛИЧНО: На сервере реальные данные!")
        print("🎉 Демо данные уже убраны!")
    else:
        print("\n⚠️ НЕ УДАЛОСЬ ПРОВЕРИТЬ СЕРВЕР")
        print("🔧 Возможно, сервер недоступен или есть проблемы с API")
        show_update_instructions()

if __name__ == "__main__":
    main()
