#!/usr/bin/env python3
"""
АККУРАТНАЯ ПРОВЕРКА СЕРВЕРА 72.56.66.228
Безопасная проверка без риска сломать что-либо
"""

import requests
import time
import json
from datetime import datetime

def safe_ping_test():
    """Безопасный ping тест"""
    print("🔍 АККУРАТНАЯ ПРОВЕРКА СЕРВЕРА 72.56.66.228")
    print("=" * 60)
    print("📡 ШАГ 1: Базовая проверка доступности...")
    
    try:
        # Очень короткий таймаут для безопасности
        response = requests.get("http://72.56.66.228", timeout=5)
        print(f"   📊 HTTP статус: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Сервер отвечает нормально")
            return "working"
        elif response.status_code == 502:
            print("   ⚠️ 502 Bad Gateway - сервер работает, но приложение не запущено")
            return "server_ok_app_down"
        elif response.status_code == 404:
            print("   ⚠️ 404 Not Found - сервер работает, но приложение не настроено")
            return "server_ok_app_missing"
        else:
            print(f"   ⚠️ Неожиданный статус: {response.status_code}")
            return "unknown"
            
    except requests.exceptions.Timeout:
        print("   ⏰ Таймаут - сервер не отвечает")
        return "timeout"
    except requests.exceptions.ConnectionError:
        print("   🔌 Ошибка подключения - сервер недоступен")
        return "connection_error"
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")
        return "error"

def safe_endpoint_check():
    """Безопасная проверка endpoints"""
    print("\n📡 ШАГ 2: Проверка основных endpoints...")
    
    # Только безопасные GET запросы
    safe_endpoints = [
        ("/", "Главная страница"),
        ("/module/trends", "Модуль трендов"),
        ("/module/vacancies", "Модуль вакансий"),
        ("/module/experts", "Модуль экспертов")
    ]
    
    working_count = 0
    
    for endpoint, description in safe_endpoints:
        try:
            # Короткий таймаут для безопасности
            response = requests.get(f"http://72.56.66.228{endpoint}", timeout=3)
            
            if response.status_code == 200:
                print(f"   ✅ {description}: работает")
                working_count += 1
            elif response.status_code == 404:
                print(f"   ⚠️ {description}: не найден (404)")
            else:
                print(f"   ⚠️ {description}: статус {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ {description}: таймаут")
        except Exception as e:
            print(f"   ❌ {description}: ошибка - {str(e)[:50]}...")
    
    return working_count

def safe_api_check():
    """Безопасная проверка API"""
    print("\n📡 ШАГ 3: Проверка API (только чтение)...")
    
    try:
        # Только безопасный GET запрос к API
        response = requests.get("http://72.56.66.228/api/competitors", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ API конкурентов: работает")
            return True
        else:
            print(f"   ⚠️ API конкурентов: статус {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ⏰ API конкурентов: таймаут")
        return False
    except Exception as e:
        print(f"   ❌ API конкурентов: ошибка - {str(e)[:50]}...")
        return False

def analyze_status(server_status, working_endpoints, api_working):
    """Анализ статуса без риска"""
    print("\n" + "=" * 60)
    print("📊 АНАЛИЗ СТАТУСА СЕРВЕРА")
    print("=" * 60)
    
    if server_status == "working":
        if working_endpoints >= 3:
            print("🎉 ОТЛИЧНО! Сервер работает полностью!")
            print("✅ Сервер доступен")
            print("✅ Приложение запущено")
            print(f"✅ Работает {working_endpoints}/4 модулей")
            if api_working:
                print("✅ API работает")
            print("\n📋 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
            return "excellent"
        else:
            print("⚠️ Сервер работает, но есть проблемы с модулями")
            print(f"✅ Работает только {working_endpoints}/4 модулей")
            return "partial"
            
    elif server_status == "server_ok_app_down":
        print("⚠️ СЕРВЕР РАБОТАЕТ, НО ПРИЛОЖЕНИЕ НЕ ЗАПУЩЕНО")
        print("🔧 НУЖНО ЗАПУСТИТЬ ПРИЛОЖЕНИЕ:")
        print("1. Подключитесь к серверу")
        print("2. Найдите папку с приложением")
        print("3. Запустите: python3 app.py")
        return "app_down"
        
    elif server_status == "server_ok_app_missing":
        print("⚠️ СЕРВЕР РАБОТАЕТ, НО ПРИЛОЖЕНИЕ НЕ НАСТРОЕНО")
        print("🔧 НУЖНО РАЗВЕРНУТЬ ПРИЛОЖЕНИЕ:")
        print("1. Загрузите файлы приложения на сервер")
        print("2. Настройте конфигурацию")
        print("3. Запустите приложение")
        return "app_missing"
        
    elif server_status == "timeout":
        print("❌ СЕРВЕР НЕ ОТВЕЧАЕТ")
        print("🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. Сервер выключен")
        print("2. Проблемы с сетью")
        print("3. Сервер перегружен")
        return "server_down"
        
    elif server_status == "connection_error":
        print("❌ ОШИБКА ПОДКЛЮЧЕНИЯ")
        print("🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. Неправильный IP адрес")
        print("2. Блокировка файрволом")
        print("3. Проблемы с DNS")
        return "connection_error"
        
    else:
        print("❓ НЕИЗВЕСТНЫЙ СТАТУС")
        print("🔧 ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА")
        return "unknown"

def show_safe_next_steps(status):
    """Безопасные следующие шаги"""
    print("\n" + "=" * 60)
    print("📋 БЕЗОПАСНЫЕ СЛЕДУЮЩИЕ ШАГИ")
    print("=" * 60)
    
    if status == "excellent":
        print("🎉 СИСТЕМА РАБОТАЕТ ОТЛИЧНО!")
        print("✅ Никаких действий не требуется")
        print("🌐 Можете использовать: http://72.56.66.228/")
        
    elif status == "partial":
        print("⚠️ СИСТЕМА РАБОТАЕТ ЧАСТИЧНО")
        print("🔧 РЕКОМЕНДАЦИИ:")
        print("1. Проверьте логи приложения")
        print("2. Убедитесь, что все модули настроены")
        print("3. Проверьте права доступа к файлам")
        
    elif status == "app_down":
        print("🔧 НУЖНО ЗАПУСТИТЬ ПРИЛОЖЕНИЕ")
        print("📋 БЕЗОПАСНЫЕ ДЕЙСТВИЯ:")
        print("1. Подключитесь к серверу через SSH")
        print("2. Найдите папку с приложением")
        print("3. Проверьте, есть ли файл app.py")
        print("4. Запустите: python3 app.py")
        print("5. Или в фоне: nohup python3 app.py > app.log 2>&1 &")
        
    elif status == "app_missing":
        print("🔧 НУЖНО РАЗВЕРНУТЬ ПРИЛОЖЕНИЕ")
        print("📋 БЕЗОПАСНЫЕ ДЕЙСТВИЯ:")
        print("1. Создайте пакет: python3 deploy_to_server.py")
        print("2. Загрузите файлы на сервер")
        print("3. Настройте конфигурацию")
        print("4. Запустите приложение")
        
    elif status in ["server_down", "connection_error"]:
        print("❌ ПРОБЛЕМЫ С СЕРВЕРОМ")
        print("📋 БЕЗОПАСНЫЕ ДЕЙСТВИЯ:")
        print("1. Проверьте доступность сервера")
        print("2. Обратитесь к администратору")
        print("3. Проверьте настройки сети")
        
    else:
        print("❓ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА")
        print("📋 БЕЗОПАСНЫЕ ДЕЙСТВИЯ:")
        print("1. Повторите проверку через несколько минут")
        print("2. Проверьте логи сервера")
        print("3. Обратитесь к администратору")

def main():
    """Основная функция - аккуратная проверка"""
    print("🛡️ АККУРАТНАЯ ПРОВЕРКА СЕРВЕРА")
    print("Безопасная проверка без риска сломать что-либо")
    print("=" * 60)
    
    # Шаг 1: Базовая проверка
    server_status = safe_ping_test()
    
    # Шаг 2: Проверка endpoints (только если сервер отвечает)
    working_endpoints = 0
    if server_status in ["working", "server_ok_app_down", "server_ok_app_missing"]:
        working_endpoints = safe_endpoint_check()
    
    # Шаг 3: Проверка API (только если сервер отвечает)
    api_working = False
    if server_status in ["working", "server_ok_app_down", "server_ok_app_missing"]:
        api_working = safe_api_check()
    
    # Анализ статуса
    status = analyze_status(server_status, working_endpoints, api_working)
    
    # Безопасные следующие шаги
    show_safe_next_steps(status)
    
    print("\n" + "=" * 60)
    print("🛡️ ПРОВЕРКА ЗАВЕРШЕНА БЕЗОПАСНО")
    print("Никаких изменений на сервере не было сделано")
    print("=" * 60)

if __name__ == "__main__":
    main()
