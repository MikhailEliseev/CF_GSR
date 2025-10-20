#!/usr/bin/env python3
"""
Быстрая и безопасная проверка сервера 72.56.66.228
"""

import requests
import time
from datetime import datetime

def quick_server_test():
    """Быстрая проверка сервера"""
    print("🔍 БЫСТРАЯ ПРОВЕРКА СЕРВЕРА 72.56.66.228")
    print("=" * 50)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Шаг 1: Базовая проверка доступности
    print("\n📡 ШАГ 1: Проверка доступности...")
    try:
        response = requests.get("http://72.56.66.228", timeout=5)
        print(f"   📊 HTTP статус: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Сервер работает нормально")
            server_status = "working"
        elif response.status_code == 502:
            print("   ⚠️ 502 Bad Gateway - приложение не запущено")
            server_status = "app_down"
        elif response.status_code == 404:
            print("   ⚠️ 404 Not Found - приложение не настроено")
            server_status = "app_missing"
        else:
            print(f"   ⚠️ Неожиданный статус: {response.status_code}")
            server_status = "unknown"
            
    except requests.exceptions.Timeout:
        print("   ⏰ Таймаут - сервер не отвечает")
        server_status = "timeout"
    except requests.exceptions.ConnectionError:
        print("   🔌 Ошибка подключения - сервер недоступен")
        server_status = "connection_error"
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        server_status = "error"
    
    # Шаг 2: Проверка модулей (только если сервер отвечает)
    if server_status in ["working", "app_down", "app_missing"]:
        print("\n📡 ШАГ 2: Проверка модулей...")
        
        modules = [
            ("/module/trends", "Модуль трендов"),
            ("/module/vacancies", "Модуль вакансий"),
            ("/module/experts", "Модуль экспертов")
        ]
        
        working_modules = 0
        for endpoint, name in modules:
            try:
                response = requests.get(f"http://72.56.66.228{endpoint}", timeout=3)
                if response.status_code == 200:
                    print(f"   ✅ {name}: работает")
                    working_modules += 1
                else:
                    print(f"   ⚠️ {name}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name}: ошибка")
        
        print(f"   📊 Работает модулей: {working_modules}/3")
    
    # Шаг 3: Итоговый анализ
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ СТАТУС")
    print("=" * 50)
    
    if server_status == "working":
        print("🎉 СЕРВЕР РАБОТАЕТ ОТЛИЧНО!")
        print("✅ Приложение запущено и доступно")
        print("🌐 Можете использовать: http://72.56.66.228/")
        
    elif server_status == "app_down":
        print("⚠️ СЕРВЕР РАБОТАЕТ, НО ПРИЛОЖЕНИЕ НЕ ЗАПУЩЕНО")
        print("🔧 НУЖНО ЗАПУСТИТЬ ПРИЛОЖЕНИЕ:")
        print("1. Подключитесь к серверу")
        print("2. Найдите папку с приложением")
        print("3. Запустите: python3 app.py")
        
    elif server_status == "app_missing":
        print("⚠️ СЕРВЕР РАБОТАЕТ, НО ПРИЛОЖЕНИЕ НЕ НАСТРОЕНО")
        print("🔧 НУЖНО РАЗВЕРНУТЬ ПРИЛОЖЕНИЕ:")
        print("1. Создайте пакет: python3 deploy_to_server.py")
        print("2. Загрузите файлы на сервер")
        print("3. Настройте и запустите приложение")
        
    elif server_status == "timeout":
        print("❌ СЕРВЕР НЕ ОТВЕЧАЕТ")
        print("🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. Сервер выключен")
        print("2. Проблемы с сетью")
        print("3. Сервер перегружен")
        
    elif server_status == "connection_error":
        print("❌ ОШИБКА ПОДКЛЮЧЕНИЯ")
        print("🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. Неправильный IP адрес")
        print("2. Блокировка файрволом")
        print("3. Проблемы с DNS")
        
    else:
        print("❓ НЕИЗВЕСТНЫЙ СТАТУС")
        print("🔧 ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА")
    
    print("\n🛡️ ПРОВЕРКА ЗАВЕРШЕНА БЕЗОПАСНО")
    print("Никаких изменений на сервере не было сделано")
    
    return server_status

if __name__ == "__main__":
    quick_server_test()
