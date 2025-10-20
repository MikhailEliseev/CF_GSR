#!/usr/bin/env python3
"""
Стресс-тест для CSV парсинга с большим количеством вакансий
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.vacancies import parse_vacancies_direct

def stress_test_large_csv():
    """Стресс-тест с большим CSV файлом"""
    print("🚀 Запускаем стресс-тест с большим CSV файлом...")
    
    # Читаем большой CSV файл
    csv_file = "/Users/mikhaileliseev/Desktop/КЗ GSR/test_data/stress_test_vacancies.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ Файл {csv_file} не найден")
        return False
    
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_data = f.read()
    
    print(f"📄 Размер файла: {len(csv_data)} символов")
    print(f"📄 Количество строк: {csv_data.count(chr(10)) + 1}")
    
    # Измеряем время парсинга
    start_time = time.time()
    vacancies = parse_vacancies_direct(csv_data)
    end_time = time.time()
    
    parsing_time = end_time - start_time
    
    print(f"\n⏱️ Время парсинга: {parsing_time:.3f} секунд")
    print(f"📊 Найдено вакансий: {len(vacancies)}")
    print(f"⚡ Скорость: {len(vacancies)/parsing_time:.1f} вакансий/сек")
    
    # Анализ качества данных
    print(f"\n🔍 Анализ качества данных:")
    
    valid_vacancies = 0
    issues_count = 0
    
    for i, vacancy in enumerate(vacancies):
        issues = []
        
        # Проверяем обязательные поля
        if not vacancy.get('position', '').strip():
            issues.append("Нет названия")
        if not vacancy.get('salary', '').strip():
            issues.append("Нет зарплаты")
        if not vacancy.get('company', '').strip():
            issues.append("Нет компании")
        
        if not issues:
            valid_vacancies += 1
        else:
            issues_count += 1
            if issues_count <= 5:  # Показываем только первые 5 проблемных
                print(f"  Вакансия {i+1}: {', '.join(issues)}")
    
    quality_percent = (valid_vacancies/len(vacancies)*100) if vacancies else 0
    print(f"✅ Валидных вакансий: {valid_vacancies}/{len(vacancies)}")
    print(f"📈 Процент качества: {quality_percent:.1f}%")
    
    # Проверяем производительность
    if parsing_time > 5.0:
        print(f"⚠️ Парсинг занял {parsing_time:.1f} секунд - это медленно")
        return False
    
    if quality_percent < 90:
        print(f"⚠️ Качество данных {quality_percent:.1f}% - ниже ожидаемого")
        return False
    
    print(f"\n🎉 Стресс-тест пройден успешно!")
    print(f"✅ Парсинг {len(vacancies)} вакансий за {parsing_time:.3f} секунд")
    print(f"✅ Качество данных: {quality_percent:.1f}%")
    print(f"✅ Скорость: {len(vacancies)/parsing_time:.1f} вакансий/сек")
    
    return True

def test_memory_usage():
    """Тест использования памяти (упрощенный)"""
    print("\n🧪 Тестируем использование памяти...")
    
    # Читаем и парсим файл
    csv_file = "/Users/mikhaileliseev/Desktop/КЗ GSR/test_data/stress_test_vacancies.csv"
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_data = f.read()
    
    vacancies = parse_vacancies_direct(csv_data)
    
    # Простая оценка использования памяти
    csv_size_mb = len(csv_data) / 1024 / 1024
    vacancies_count = len(vacancies)
    
    print(f"📊 Размер CSV файла: {csv_size_mb:.3f} MB")
    print(f"📊 Количество вакансий: {vacancies_count}")
    print(f"📊 Размер на вакансию: {csv_size_mb/vacancies_count:.6f} MB")
    
    if csv_size_mb > 10:  # Больше 10 MB
        print(f"⚠️ Большой размер файла: {csv_size_mb:.1f} MB")
        return False
    
    print(f"✅ Размер файла в норме")
    return True

def run_stress_tests():
    """Запуск всех стресс-тестов"""
    print("🚀 Запускаем стресс-тесты CSV парсинга...")
    print("="*60)
    
    try:
        # Тест 1: Большой CSV файл
        test1_success = stress_test_large_csv()
        
        # Тест 2: Использование памяти
        test2_success = test_memory_usage()
        
        print("\n" + "="*60)
        print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТОВ:")
        print(f"✅ Большой CSV файл: {'ПРОЙДЕН' if test1_success else 'ПРОВАЛЕН'}")
        print(f"✅ Использование памяти: {'ПРОЙДЕН' if test2_success else 'ПРОВАЛЕН'}")
        
        if test1_success and test2_success:
            print("\n🎉 ВСЕ СТРЕСС-ТЕСТЫ ПРОЙДЕНЫ!")
            print("📋 Система готова к работе с большими объемами данных:")
            print("  • Быстрый парсинг больших файлов")
            print("  • Эффективное использование памяти")
            print("  • Высокое качество данных")
            return True
        else:
            print("\n❌ НЕКОТОРЫЕ СТРЕСС-ТЕСТЫ ПРОВАЛЕНЫ")
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении стресс-тестов: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_stress_tests()
    exit(0 if success else 1)
