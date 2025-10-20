#!/usr/bin/env python3
"""
Прямая проверка сервера 72.56.66.228
Безопасная проверка без риска
"""

import requests
import time
from datetime import datetime

def direct_server_check():
    """Прямая проверка сервера"""
    print("🔍 ПРЯМАЯ ПРОВЕРКА СЕРВЕРА 72.56.66.228")
    print("=" * 60)
    print(f"⏰ Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Шаг 1: Базовая проверка доступности
    print("\n📡 ШАГ 1: Базовая проверка доступности...")
    print("   🔗 URL: http://72.56.66.228")
    print("   ⏱️ Таймаут: 5 секунд")
    
    try:
        response = requests.get("http://72.56.66.228", timeout=5)
        print(f"   📊 HTTP статус: {response.status_code}")
        print(f"   📏 Размер ответа: {len(response.content)} байт")
        
        if response.status_code == 200:
            print("   ✅ Сервер работает нормально")
            print("   📄 Приложение доступно")
            server_status = "working"
            
        elif response.status_code == 502:
            print("   ⚠️ 502 Bad Gateway")
            print("   🔧 Сервер работает, но приложение не запущено")
            server_status = "app_down"
            
        elif response.status_code == 404:
            print("   ⚠️ 404 Not Found")
            print("   🔧 Сервер работает, но приложение не настроено")
            server_status = "app_missing"
            
        elif response.status_code == 503:
            print("   ⚠️ 503 Service Unavailable")
            print("   🔧 Сервер перегружен или недоступен")
            server_status = "overloaded"
            
        else:
            print(f"   ⚠️ Неожиданный статус: {response.status_code}")
            server_status = "unknown"
            
    except requests.exceptions.Timeout:
        print("   ⏰ Таймаут - сервер не отвечает за 5 секунд")
        print("   🔧 Возможные причины: перегрузка, проблемы с сетью")
        server_status = "timeout"
        
    except requests.exceptions.ConnectionError:
        print("   🔌 Ошибка подключения - сервер недоступен")
        print("   🔧 Возможные причины: сервер выключен, блокировка файрволом")
        server_status = "connection_error"
        
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")
        server_status = "error"
    
    # Шаг 2: Проверка модулей (только если сервер отвечает)
    if server_status in ["working", "app_down", "app_missing"]:
        print("\n📡 ШАГ 2: Проверка модулей приложения...")
        
        modules = [
            ("/", "Главная страница"),
            ("/module/trends", "Модуль трендов"),
            ("/module/vacancies", "Модуль вакансий"),
            ("/module/experts", "Модуль экспертов")
        ]
        
        working_modules = 0
        for endpoint, name in modules:
            try:
                print(f"   🔍 Проверяем {name}...")
                response = requests.get(f"http://72.56.66.228{endpoint}", timeout=3)
                
                if response.status_code == 200:
                    print(f"   ✅ {name}: работает ({response.status_code})")
                    working_modules += 1
                elif response.status_code == 404:
                    print(f"   ⚠️ {name}: не найден (404)")
                else:
                    print(f"   ⚠️ {name}: статус {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ {name}: таймаут")
            except Exception as e:
                print(f"   ❌ {name}: ошибка - {str(e)[:30]}...")
        
        print(f"   📊 Работает модулей: {working_modules}/{len(modules)}")
    
    # Шаг 3: Проверка API (только если сервер отвечает)
    if server_status in ["working", "app_down", "app_missing"]:
        print("\n📡 ШАГ 3: Проверка API...")
        
        try:
            print("   🔍 Проверяем API конкурентов...")
            response = requests.get("http://72.56.66.228/api/competitors", timeout=3)
            
            if response.status_code == 200:
                print("   ✅ API конкурентов: работает")
                api_working = True
            else:
                print(f"   ⚠️ API конкурентов: статус {response.status_code}")
                api_working = False
                
        except requests.exceptions.Timeout:
            print("   ⏰ API конкурентов: таймаут")
            api_working = False
        except Exception as e:
            print(f"   ❌ API конкурентов: ошибка - {str(e)[:30]}...")
            api_working = False
    else:
        api_working = False
    
    # Шаг 4: Итоговый анализ
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ АНАЛИЗ СТАТУСА")
    print("=" * 60)
    
    if server_status == "working":
        print("🎉 ОТЛИЧНО! СЕРВЕР РАБОТАЕТ ПОЛНОСТЬЮ!")
        print("✅ Сервер доступен")
        print("✅ Приложение запущено")
        print("✅ Веб-интерфейс работает")
        if api_working:
            print("✅ API работает")
        print("\n🌐 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
        print("🔗 URL: http://72.56.66.228/")
        
    elif server_status == "app_down":
        print("⚠️ СЕРВЕР РАБОТАЕТ, НО ПРИЛОЖЕНИЕ НЕ ЗАПУЩЕНО")
        print("🔧 НУЖНО ЗАПУСТИТЬ ПРИЛОЖЕНИЕ:")
        print("1. Подключитесь к серверу через SSH")
        print("2. Найдите папку с приложением")
        print("3. Запустите: python3 app.py")
        print("4. Или в фоне: nohup python3 app.py > app.log 2>&1 &")
        
    elif server_status == "app_missing":
        print("⚠️ СЕРВЕР РАБОТАЕТ, НО ПРИЛОЖЕНИЕ НЕ НАСТРОЕНО")
        print("🔧 НУЖНО РАЗВЕРНУТЬ ПРИЛОЖЕНИЕ:")
        print("1. Создайте пакет: python3 deploy_to_server.py")
        print("2. Загрузите файлы на сервер")
        print("3. Настройте конфигурацию")
        print("4. Запустите приложение")
        
    elif server_status == "overloaded":
        print("⚠️ СЕРВЕР ПЕРЕГРУЖЕН")
        print("🔧 РЕКОМЕНДАЦИИ:")
        print("1. Подождите несколько минут")
        print("2. Проверьте загрузку сервера")
        print("3. Обратитесь к администратору")
        
    elif server_status == "timeout":
        print("❌ СЕРВЕР НЕ ОТВЕЧАЕТ")
        print("🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. Сервер выключен")
        print("2. Проблемы с сетью")
        print("3. Сервер перегружен")
        print("4. Блокировка файрволом")
        
    elif server_status == "connection_error":
        print("❌ ОШИБКА ПОДКЛЮЧЕНИЯ")
        print("🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. Неправильный IP адрес")
        print("2. Блокировка файрволом")
        print("3. Проблемы с DNS")
        print("4. Сервер выключен")
        
    else:
        print("❓ НЕИЗВЕСТНЫЙ СТАТУС")
        print("🔧 ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА")
    
    print("\n🛡️ ПРОВЕРКА ЗАВЕРШЕНА БЕЗОПАСНО")
    print("Никаких изменений на сервере не было сделано")
    print("=" * 60)
    
    return server_status

if __name__ == "__main__":
    direct_server_check()
