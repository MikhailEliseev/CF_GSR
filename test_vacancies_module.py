#!/usr/bin/env python3
"""
Тестирование модуля вакансий
Проверяет полный цикл: парсинг → выбор → генерация текста → аудио → видео
"""

import requests
import json
import time

# Конфигурация
BASE_URL = "http://72.56.66.228"
# BASE_URL = "http://localhost:5000"  # Для локального тестирования

def test_vacancies_endpoints():
    """Тестирует все endpoints модуля вакансий"""
    print("🧪 Тестирование модуля вакансий")
    print("=" * 50)
    
    # 1. Тест получения тестовых вакансий
    print("\n1️⃣ Тестируем /api/vacancies/test")
    try:
        response = requests.get(f"{BASE_URL}/api/vacancies/test", timeout=10)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Успех: получено {len(data.get('vacancies', []))} тестовых вакансий")
            
            # Показываем первую вакансию
            if data.get('vacancies'):
                first_vacancy = data['vacancies'][0]
                print(f"   📋 Первая вакансия: {first_vacancy.get('title', 'Без названия')}")
                print(f"   🏢 Компания: {first_vacancy.get('company', 'Не указано')}")
                print(f"   💰 Зарплата: {first_vacancy.get('salary', 'Не указано')}")
        else:
            print(f"   ❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Исключение: {str(e)}")
    
    # 2. Тест парсинга Google Sheets (с тестовым URL)
    print("\n2️⃣ Тестируем /api/vacancies/parse")
    test_sheets_url = "https://docs.google.com/spreadsheets/d/1I1AfpmNbd-K0Osd4Vh7npDCYSQr2a1t_KdT8ms9vgr4/edit?gid=718924971#gid=718924971"
    
    try:
        payload = {"url": test_sheets_url}
        response = requests.post(
            f"{BASE_URL}/api/vacancies/parse", 
            json=payload, 
            timeout=30
        )
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Успех: распарсено {len(data.get('vacancies', []))} вакансий")
                
                # Показываем первую вакансию
                if data.get('vacancies'):
                    first_vacancy = data['vacancies'][0]
                    print(f"   📋 Первая вакансия: {first_vacancy.get('title', 'Без названия')}")
                    print(f"   🏢 Объект: {first_vacancy.get('object', 'Не указано')}")
            else:
                print(f"   ❌ Ошибка парсинга: {data.get('error', 'Неизвестная ошибка')}")
        else:
            print(f"   ❌ HTTP ошибка: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Исключение: {str(e)}")
    
    # 3. Тест генерации текста
    print("\n3️⃣ Тестируем /api/vacancies/generate-text")
    test_vacancy = {
        "title": "Сборщик на конвейере",
        "object": "ЛГ Электроникс - производство техники",
        "salary": "320 руб/час, 30 смен - 105600 руб",
        "conditions": "смена - 11 часов, Вахта: 30/45 смен",
        "requirements": "От 18 до 45 лет, РФ/ЕАЭС",
        "benefits": "Сборка бытовой техники, чистое производство",
        "positions_needed": "15 муж.",
        "manager": "Константин Тренин",
        "company": "ООО\"Фортренд\"",
        "company_benefits": "Удаленное оформление, 25 офисов"
    }
    
    try:
        payload = {"vacancy": test_vacancy}
        response = requests.post(
            f"{BASE_URL}/api/vacancies/generate-text", 
            json=payload, 
            timeout=30
        )
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                text = data.get('text', '')
                print(f"   ✅ Успех: сгенерирован текст ({len(text)} символов)")
                print(f"   📝 Превью: {text[:200]}...")
            else:
                print(f"   ❌ Ошибка генерации: {data.get('error', 'Неизвестная ошибка')}")
        else:
            print(f"   ❌ HTTP ошибка: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Исключение: {str(e)}")
    
    # 4. Тест общих endpoints (аудио и видео)
    print("\n4️⃣ Тестируем общие endpoints")
    
    # Тест ElevenLabs voices
    try:
        response = requests.get(f"{BASE_URL}/api/elevenlabs/voices", timeout=10)
        print(f"   ElevenLabs voices: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Голоса: {len(data.get('voices', []))} доступно")
    except Exception as e:
        print(f"   ❌ ElevenLabs voices: {str(e)}")
    
    # Тест HeyGen avatars
    try:
        response = requests.get(f"{BASE_URL}/api/heygen/avatars", timeout=10)
        print(f"   HeyGen avatars: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Аватары: {len(data.get('avatars', []))} доступно")
    except Exception as e:
        print(f"   ❌ HeyGen avatars: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Тестирование завершено!")

def test_frontend_access():
    """Тестирует доступность frontend страницы"""
    print("\n🌐 Тестирование frontend")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/module_vacancies", timeout=10)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Страница модуля вакансий доступна")
            
            # Проверяем наличие ключевых элементов
            content = response.text
            if "Модуль Вакансий" in content:
                print("   ✅ Заголовок найден")
            if "vacanciesTable" in content:
                print("   ✅ Таблица вакансий найдена")
            if "DataTables" in content:
                print("   ✅ DataTables подключен")
            if "selectVacancyFromTable" in content:
                print("   ✅ Функция выбора из таблицы найдена")
        else:
            print(f"   ❌ Ошибка доступа: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Исключение: {str(e)}")

if __name__ == "__main__":
    print("🚀 Запуск тестирования модуля вакансий")
    print(f"🎯 Целевой сервер: {BASE_URL}")
    
    test_vacancies_endpoints()
    test_frontend_access()
    
    print("\n📋 Инструкции для ручного тестирования:")
    print("1. Откройте http://72.56.66.228/module_vacancies")
    print("2. Нажмите 'Тестовые данные' для загрузки тестовых вакансий")
    print("3. Выберите вакансию в таблице")
    print("4. Нажмите 'Получить текст от ИИ-ассистента'")
    print("5. Создайте аудио и видео через общий pipeline")
