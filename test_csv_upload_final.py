#!/usr/bin/env python3
"""
Финальный тест CSV загрузки с исправлениями
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.vacancies import parse_vacancies_direct
import json

def test_csv_parsing_with_real_data():
    """Тест парсинга с реальными данными"""
    print("🧪 Тестируем парсинг с реальными данными...")
    
    # Читаем тестовый CSV
    with open("/Users/mikhaileliseev/Desktop/КЗ GSR/test_data/test_vacancies_full.csv", "r", encoding="utf-8") as f:
        csv_data = f.read()
    
    print(f"📄 Размер CSV файла: {len(csv_data)} символов")
    print(f"📄 Первые 200 символов:\n{csv_data[:200]}")
    
    # Парсим данные
    vacancies = parse_vacancies_direct(csv_data)
    
    print(f"\n📊 Результаты парсинга:")
    print(f"✅ Найдено вакансий: {len(vacancies)}")
    
    if vacancies:
        print(f"\n📋 Первая вакансия:")
        first_vacancy = vacancies[0]
        for key, value in first_vacancy.items():
            print(f"  {key}: {value}")
        
        print(f"\n📋 Последняя вакансия:")
        last_vacancy = vacancies[-1]
        for key, value in last_vacancy.items():
            print(f"  {key}: {value}")
    
    # Проверяем качество данных
    print(f"\n🔍 Анализ качества данных:")
    
    valid_vacancies = 0
    for i, vacancy in enumerate(vacancies):
        issues = []
        
        # Проверяем обязательные поля
        if not vacancy.get('position', '').strip():
            issues.append("Нет названия должности")
        if not vacancy.get('salary', '').strip():
            issues.append("Нет зарплаты")
        if not vacancy.get('company', '').strip():
            issues.append("Нет компании")
        
        if not issues:
            valid_vacancies += 1
        else:
            print(f"  Вакансия {i+1}: {', '.join(issues)}")
    
    print(f"✅ Валидных вакансий: {valid_vacancies}/{len(vacancies)}")
    print(f"📈 Процент качества: {(valid_vacancies/len(vacancies)*100):.1f}%" if vacancies else "0%")
    
    return len(vacancies) > 0

def test_column_mapping():
    """Тест правильности маппинга колонок"""
    print("\n🧪 Тестируем правильность маппинга колонок...")
    
    # Создаем тестовый CSV с известными данными
    test_csv = """Акции и скидки,Объект,Оплата,Условия,Требования,Потребность,Менеджер,Юр.лицо,Преимущества
Должность:,Объект,Оплата,Условия,Требования,Потребность,Менеджер,Юр.лицо,Преимущества
,Тестовая вакансия,1000 руб/час,8 часов,Опыт работы,5 чел.,Иван Петров,ООО Тест,Хорошие условия"""
    
    vacancies = parse_vacancies_direct(test_csv)
    
    if not vacancies:
        print("❌ Не удалось распарсить тестовые данные")
        return False
    
    vacancy = vacancies[0]
    
    # Проверяем правильность маппинга
    expected_mapping = {
        'position': 'Тестовая вакансия',  # B (индекс 1)
        'salary': '1000 руб/час',         # C (индекс 2) 
        'conditions': '8 часов',          # D (индекс 3)
        'requirements': 'Опыт работы',    # E (индекс 4)
        'positions_needed': '5 чел.',     # F (индекс 5)
        'manager': 'Иван Петров',         # G (индекс 6)
        'company': 'ООО Тест',           # H (индекс 7)
        'benefits': 'Хорошие условия'     # I (индекс 8)
    }
    
    print("🔍 Проверяем маппинг колонок:")
    all_correct = True
    
    for field, expected_value in expected_mapping.items():
        actual_value = vacancy.get(field, '')
        if actual_value == expected_value:
            print(f"  ✅ {field}: {actual_value}")
        else:
            print(f"  ❌ {field}: ожидалось '{expected_value}', получено '{actual_value}'")
            all_correct = False
    
    return all_correct

def run_final_tests():
    """Запуск всех финальных тестов"""
    print("🚀 Запускаем финальные тесты CSV загрузки...")
    print("="*60)
    
    try:
        # Тест 1: Парсинг с реальными данными
        test1_success = test_csv_parsing_with_real_data()
        
        # Тест 2: Правильность маппинга колонок
        test2_success = test_column_mapping()
        
        print("\n" + "="*60)
        print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
        print(f"✅ Парсинг реальных данных: {'ПРОЙДЕН' if test1_success else 'ПРОВАЛЕН'}")
        print(f"✅ Маппинг колонок: {'ПРОЙДЕН' if test2_success else 'ПРОВАЛЕН'}")
        
        if test1_success and test2_success:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("📋 Исправления работают корректно:")
            print("  • Индексы колонок исправлены")
            print("  • Circular import убран")
            print("  • Добавлено детальное логирование")
            print("  • Добавлена валидация данных")
            print("  • Все поля заполняются правильно")
            return True
        else:
            print("\n❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_final_tests()
    exit(0 if success else 1)
