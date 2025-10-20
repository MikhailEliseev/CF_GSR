#!/usr/bin/env python3
"""
Тест ВСЕХ полей после исправления всех индексов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.vacancies import parse_vacancies_direct

def test_all_fields():
    """Тестируем что все поля теперь берутся из правильных колонок"""
    
    # Создаем тестовый CSV с известными данными
    test_csv = """Акции и скидки,Объект,Оплата,Условия,Требования,Потребность,Менеджер,Юр.лицо,Преимущества
Должность:,Объект,Оплата,Условия,Требования,Потребность,Менеджер,Юр.лицо,Преимущества
,Сборщик на конвейере,320 руб/час,смена - 11 часов,От 18 до 45 лет,15 муж.,Константин Тренин,ООО Фортренд,Сборка бытовой техники"""
    
    print("🧪 Тестируем ВСЕ поля после исправления...")
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
    print(f"  location: '{vacancy['location']}'")
    print(f"  salary: '{vacancy['salary']}'")
    print(f"  conditions: '{vacancy['conditions']}'")
    print(f"  requirements: '{vacancy['requirements']}'")
    print(f"  positions_needed: '{vacancy['positions_needed']}'")
    print(f"  manager: '{vacancy['manager']}'")
    print(f"  company: '{vacancy['company']}'")
    print(f"  benefits: '{vacancy['benefits']}'")
    print()
    
    # Ожидаемые значения
    expected = {
        'position': 'Сборщик на конвейере',  # B
        'location': 'Сборщик на конвейере',  # B
        'salary': '320 руб/час',             # C
        'conditions': 'смена - 11 часов',   # D
        'requirements': 'От 18 до 45 лет',   # E
        'positions_needed': '15 муж.',       # F
        'manager': 'Константин Тренин',     # G
        'company': 'ООО Фортренд',          # H
        'benefits': 'Сборка бытовой техники' # I
    }
    
    print("🎯 Проверяем все поля:")
    all_correct = True
    
    for field, expected_value in expected.items():
        actual_value = vacancy[field]
        if actual_value == expected_value:
            print(f"  ✅ {field}: '{actual_value}'")
        else:
            print(f"  ❌ {field}: ожидалось '{expected_value}', получено '{actual_value}'")
            all_correct = False
    
    print()
    if all_correct:
        print("🎉 ВСЕ ПОЛЯ ИСПРАВЛЕНЫ! Все данные берутся из правильных колонок!")
        return True
    else:
        print("💥 Некоторые поля всё ещё неправильные")
        return False

if __name__ == "__main__":
    success = test_all_fields()
    if success:
        print("\n🎉 ВСЕ ИСПРАВЛЕНИЯ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("\n💥 Есть ошибки в исправлениях!")
    sys.exit(0 if success else 1)
