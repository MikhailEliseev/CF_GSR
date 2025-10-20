#!/usr/bin/env python3
"""
Скрипт для проверки успешного развертывания на сервере
"""

import requests
import time
from datetime import datetime

def check_deployment():
    """Проверка развертывания на сервере"""
    print("🔍 ПРОВЕРКА РАЗВЕРТЫВАНИЯ КОНТЕНТ-ЗАВОДА")
    print("=" * 50)
    
    server_url = "http://72.56.66.228"
    endpoints_to_check = [
        ("/", "Главная страница"),
        ("/status", "Статус приложения"),
        ("/api/trends", "API трендов"),
        ("/api/vacancies", "API вакансий"),
        ("/api/experts", "API экспертов")
    ]
    
    results = {}
    
    for endpoint, description in endpoints_to_check:
        url = f"{server_url}{endpoint}"
        print(f"\n🔍 Проверка {description}: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            status_code = response.status_code
            
            if status_code == 200:
                print(f"✅ {description}: OK (200)")
                results[endpoint] = "OK"
            elif status_code == 404:
                print(f"⚠️  {description}: Не найдено (404)")
                results[endpoint] = "404"
            elif status_code == 502:
                print(f"❌ {description}: Bad Gateway (502)")
                results[endpoint] = "502"
            else:
                print(f"⚠️  {description}: Статус {status_code}")
                results[endpoint] = f"Status {status_code}"
                
        except requests.exceptions.Timeout:
            print(f"⏰ {description}: Таймаут")
            results[endpoint] = "Timeout"
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Ошибка подключения")
            results[endpoint] = "Connection Error"
        except Exception as e:
            print(f"❌ {description}: Ошибка - {e}")
            results[endpoint] = f"Error: {e}"
    
    return results

def analyze_results(results):
    """Анализ результатов проверки"""
    print("\n" + "=" * 50)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("=" * 50)
    
    ok_count = sum(1 for status in results.values() if status == "OK")
    total_count = len(results)
    
    print(f"✅ Работающих endpoints: {ok_count}/{total_count}")
    
    if ok_count == total_count:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
        print("✅ Контент-завод полностью развернут и работает")
        return "success"
    elif ok_count > 0:
        print("⚠️  ЧАСТИЧНО РАБОТАЕТ")
        print("✅ Основные компоненты работают")
        print("⚠️  Некоторые endpoints требуют внимания")
        return "partial"
    else:
        print("❌ ПРОБЛЕМЫ С РАЗВЕРТЫВАНИЕМ")
        print("❌ Приложение не отвечает или не запущено")
        return "failed"

def show_next_steps(status):
    """Показать следующие шаги в зависимости от статуса"""
    print("\n" + "=" * 50)
    print("📋 СЛЕДУЮЩИЕ ШАГИ")
    print("=" * 50)
    
    if status == "success":
        print("🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("\n✅ Что работает:")
        print("- Главная страница")
        print("- API endpoints")
        print("- Все модули")
        print("\n🚀 Система готова к использованию!")
        
    elif status == "partial":
        print("⚠️  ЧАСТИЧНОЕ РАЗВЕРТЫВАНИЕ")
        print("\n🔧 Что нужно проверить:")
        print("1. Логи приложения на сервере")
        print("2. Настройки базы данных")
        print("3. API ключи")
        print("4. Права доступа к файлам")
        
    else:
        print("❌ ПРОБЛЕМЫ С РАЗВЕРТЫВАНИЕМ")
        print("\n🔧 Что нужно сделать:")
        print("1. Проверить, что приложение запущено на сервере")
        print("2. Проверить логи nginx")
        print("3. Проверить настройки прокси")
        print("4. Убедиться, что все зависимости установлены")

def main():
    print(f"🕐 Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверка развертывания
    results = check_deployment()
    
    # Анализ результатов
    status = analyze_results(results)
    
    # Следующие шаги
    show_next_steps(status)
    
    print(f"\n🕐 Проверка завершена: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
