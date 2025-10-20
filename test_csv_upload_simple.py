#!/usr/bin/env python3
"""
Простой тест загрузки CSV
"""

import requests
import json

def test_csv_upload():
    """Тестируем загрузку CSV"""
    print("🧪 Тестируем загрузку CSV...")
    
    try:
        # Создаем тестовый CSV файл
        test_csv_content = """A,B,C,D,E,F,G,H,I
Должность:,Объект,Оплата,Условия,Требования,Потребность,Менеджер,Юр.лицо,Преимущества
,Сборщик на конвейере,ЛГ Электроникс,320 руб/час,смена - 11 часов,От 18 до 45 лет,15 муж.,Константин Тренин,ООО Фортренд,Сборка бытовой техники
,Работник склада,ДжамильКо,370 руб/час,смена - 11 часов,РФ/РБ,0,Виктор Горяинов,ООО Фортренд,Брендовая одежда"""
        
        # Сохраняем тестовый файл
        with open("test_vacancies.csv", "w", encoding="utf-8") as f:
            f.write(test_csv_content)
        
        print("✅ Тестовый CSV файл создан")
        
        # Тестируем загрузку
        with open("test_vacancies.csv", "rb") as f:
            files = {"file": ("test_vacancies.csv", f, "text/csv")}
            
            response = requests.post(
                "http://72.56.66.228/api/vacancies/upload-csv",
                files=files
            )
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Ответ: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ CSV загружен успешно! Найдено {data.get('count', 0)} вакансий")
                return True
            else:
                print(f"❌ Ошибка: {data.get('error', 'Неизвестная ошибка')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_csv_upload()
    if success:
        print("\n🎉 CSV загрузка работает!")
        print("Проблема может быть в frontend коде или в том, что пользователь нажимает неправильную кнопку")
    else:
        print("\n❌ CSV загрузка не работает")
        print("Нужно проверить сервер и endpoint")
