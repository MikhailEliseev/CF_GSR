#!/usr/bin/env python3
"""
Тест ТОЛЬКО salary после исправления row[3] → row[2]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.vacancies import parse_vacancies_direct

def test_salary_fix():
    """Тестируем что salary теперь берется из правильной колонки"""
    
    # Создаем тестовый CSV с известными данными
    test_csv = """Акции и скидки,Объект,Оплата,Условия,Требования,Потребность,Менеджер,Юр.лицо,Преимущества
Должность:,Объект,Оплата,Условия,Требования,Потребность,Менеджер,Юр.лицо,Преимущества
,Сборщик на конвейере,320 руб/час,смена - 11 часов,От 18 до 45 лет,15 муж.,Константин Тренин,ООО Фортренд,Сборка бытовой техники"""
    
    print("🧪 Тестируем исправление salary...")
    print("CSV структура:")
    print("A: Акции, B: Объект, C: Оплата, D: Условия, E: Требования, F: Потребность, G: Менеджер, H: Юр.лицо, I: Преимущества")
    print()
    
    # Парсим CSV
    vacancies = parse_vacancies_direct(test_csv)
    
    if not vacancies:
        print("❌ Не найдено вакансий!")
        return False
    
    vacancy = vacancies[0]
    print(f"📋 Результат парсинга:")
    print(f"  position: '{vacancy['position']}'")
    print(f"  salary: '{vacancy['salary']}'")
    print(f"  conditions: '{vacancy['conditions']}'")
    print(f"  requirements: '{vacancy['requirements']}'")
    print()
    
    # Проверяем salary
    expected_salary = "320 руб/час"
    actual_salary = vacancy['salary']
    
    print(f"🎯 Проверяем salary:")
    print(f"  Ожидаемо: '{expected_salary}'")
    print(f"  Получено: '{actual_salary}'")
    
    if actual_salary == expected_salary:
        print("✅ SALARY ИСПРАВЛЕН! Теперь берется из колонки C")
        return True
    else:
        print("❌ Salary всё ещё неправильный")
        return False

if __name__ == "__main__":
    success = test_salary_fix()
    if success:
        print("\n🎉 Шаг 1.1 ПРОЙДЕН: Salary исправлен!")
    else:
        print("\n💥 Шаг 1.1 ПРОВАЛЕН: Salary не исправлен!")
    sys.exit(0 if success else 1)
