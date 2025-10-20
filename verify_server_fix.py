#!/usr/bin/env python3
"""
Проверка сервера после обновления - убеждаемся, что демо данные убраны
"""

import requests
import json
import time

def check_server_fix():
    """Проверяет, что демо данные убраны с сервера"""
    print("🔍 ПРОВЕРКА СЕРВЕРА ПОСЛЕ ОБНОВЛЕНИЯ")
    print("="*50)
    
    try:
        print("📡 Подключаемся к серверу...")
        
        # Тестируем сбор рилсов
        response = requests.post(
            "http://72.56.66.228/api/trends/collect-reels",
            json={
                "competitors": ["rem.vac"],
                "count": 5
            },
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API работает: {data.get('success', False)}")
            
            if data.get('success'):
                reels = data.get('reels', [])
                print(f"📋 Получено рилсов: {len(reels)}")
                
                if reels:
                    # Проверяем первый рилс
                    first_reel = reels[0]
                    caption = first_reel.get('caption', '')
                    date = first_reel.get('timestamp', '')
                    source = first_reel.get('source_username', '')
                    
                    print(f"\n🔍 АНАЛИЗ ПЕРВОГО РИЛСА:")
                    print(f"   Источник: @{source}")
                    print(f"   Описание: {caption[:100]}...")
                    print(f"   Дата: {date}")
                    
                    # Проверяем признаки демо данных
                    demo_indicators = [
                        'демо', 'demo', 'ДЕМО', 'DEMO',
                        'пример контента',
                        '21.01.1970',
                        'demo_'
                    ]
                    
                    is_demo = any(indicator in caption.lower() for indicator in demo_indicators)
                    is_old_date = '1970' in str(date)
                    
                    if is_demo or is_old_date:
                        print("\n❌ ОШИБКА: ДЕМО ДАННЫЕ ВСЕ ЕЩЕ ЕСТЬ!")
                        print("🔧 Сервер не обновлен или обновлен неправильно")
                        return False
                    else:
                        print("\n✅ ОТЛИЧНО: ДЕМО ДАННЫЕ УБРАНЫ!")
                        print("🎉 Сервер обновлен успешно")
                        return True
                else:
                    print("\n⚠️ Сервер не вернул рилсов")
                    print("🔧 Возможно, проблема с Apify API")
                    return None
            else:
                print(f"\n❌ Ошибка API: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"\n❌ HTTP ошибка: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n⏰ ТАЙМАУТ: Сервер не отвечает")
        print("🔧 Возможно, приложение не запущено")
        return None
    except requests.exceptions.ConnectionError:
        print("\n🔌 ОШИБКА ПОДКЛЮЧЕНИЯ: Сервер недоступен")
        print("🔧 Проверьте, что сервер запущен")
        return None
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {e}")
        return None

def show_next_steps(is_fixed):
    """Показывает следующие шаги в зависимости от результата"""
    print("\n" + "="*60)
    
    if is_fixed is True:
        print("🎉 СЕРВЕР УСПЕШНО ОБНОВЛЕН!")
        print("="*60)
        print()
        print("✅ Демо данные убраны")
        print("✅ Реальные данные от Apify API")
        print("✅ Система готова к использованию")
        print()
        print("🚀 ЧТО ДАЛЬШЕ:")
        print("1. Откройте http://72.56.66.228/module/trends")
        print("2. Настройте API ключи в разделе 'Настройки API'")
        print("3. Протестируйте полный пайплайн")
        print("4. Начните создавать контент!")
        
    elif is_fixed is False:
        print("❌ СЕРВЕР НЕ ОБНОВЛЕН!")
        print("="*60)
        print()
        print("🔧 ЧТО НУЖНО СДЕЛАТЬ:")
        print("1. Подключитесь к серверу: ssh user@72.56.66.228")
        print("2. Замените app.py на app_for_server.py")
        print("3. Перезапустите приложение")
        print("4. Запустите этот тест снова")
        print()
        print("📁 ФАЙЛЫ ДЛЯ ОБНОВЛЕНИЯ:")
        print("✅ app_for_server.py - ВЕРСИЯ БЕЗ ДЕМО ДАННЫХ")
        print("✅ SERVER_DEMO_FIX_INSTRUCTIONS.md - Инструкция")
        
    else:
        print("⚠️ НЕ УДАЛОСЬ ПРОВЕРИТЬ СЕРВЕР")
        print("="*60)
        print()
        print("🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. Сервер недоступен")
        print("2. Приложение не запущено")
        print("3. Проблемы с API")
        print()
        print("🚀 ЧТО ДЕЛАТЬ:")
        print("1. Проверьте доступность сервера")
        print("2. Убедитесь, что приложение запущено")
        print("3. Проверьте логи: tail -f app.log")

def main():
    print("🚀 ПРОВЕРКА ОБНОВЛЕНИЯ СЕРВЕРА")
    print("Убираем демо данные из модуля трендов")
    print()
    
    # Проверяем сервер
    is_fixed = check_server_fix()
    
    # Показываем следующие шаги
    show_next_steps(is_fixed)
    
    print("\n" + "="*60)
    print("📞 ЕСЛИ ВОЗНИКНУТ ПРОБЛЕМЫ:")
    print("1. Проверьте SERVER_DEMO_FIX_INSTRUCTIONS.md")
    print("2. Убедитесь, что файл app.py заменен")
    print("3. Проверьте, что приложение перезапущено")
    print("4. Проверьте API ключи в настройках")

if __name__ == "__main__":
    main()
