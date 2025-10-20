import csv
from io import StringIO
import os

def parse_vacancies_direct(csv_data):
    """Прямой парсинг CSV с пропуском акций и заголовков"""
    import csv
    from io import StringIO
    
    try:
        reader = csv.reader(StringIO(csv_data))
        vacancies = []
        skipped_rows = 0
        
        print(f"Начинаем парсинг CSV, размер: {len(csv_data)} символов")
        
        for i, row in enumerate(reader):
            try:
                # Пропускаем первые 2 строки: акции и заголовки
                if i == 0:  # Пропускаем акции
                    skipped_rows += 1
                    print(f"Пропускаем строку {i}: акции")
                    continue
                if i == 1:  # Пропускаем заголовки
                    skipped_rows += 1
                    print(f"Пропускаем строку {i}: заголовки")
                    continue
                
                # Проверяем что это вакансия, а не метаданные
                if not row[1].strip():  # Нет объекта - пропускаем
                    continue
                if 'Должность' in row[0] or 'Пол' in row[0]:  # Заголовки - пропускаем
                    continue
                
                # Извлекаем все поля с правильными индексами
                vacancy = {
                    'position': row[1].strip() if len(row) > 1 else '',  # Колонка B - Объект (должность)
                    'location': row[1].strip() if len(row) > 1 else '',  # Колонка B - Объект
                    'salary': row[3].strip() if len(row) > 3 else '',    # Колонка D - Оплата
                    'conditions': row[4].strip() if len(row) > 4 else '', # Колонка E - Условия
                    'requirements': row[5].strip() if len(row) > 5 else '', # Колонка F - Требования
                    'positions_needed': row[6].strip() if len(row) > 6 else '', # Колонка G - Потребность
                    'manager': row[7].strip() if len(row) > 7 else '',   # Колонка H - Менеджер
                    'company': row[8].strip() if len(row) > 8 else '',   # Колонка I - Юр.лицо
                    'benefits': row[9].strip() if len(row) > 9 else ''   # Колонка J - Преимущества
                }
                vacancies.append(vacancy)
                print(f"Добавлена вакансия {len(vacancies)}: {vacancy['location'][:30]}...")
                
            except Exception as e:
                print(f"Ошибка парсинга строки {i}: {e}")
                continue
        
        print(f"Пропущено строк: {skipped_rows}")
        print(f"Распарсено вакансий: {len(vacancies)}")
        return vacancies
        
    except Exception as e:
        print(f"Ошибка парсинга CSV: {e}")
        return []

if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    csv_file_path = os.path.join(script_dir, 'test_data', 'real_vacancies.csv')
    
    print("🧪 Тестируем улучшенный парсинг вакансий...")
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        csv_data = f.read()
    
    result = parse_vacancies_direct(csv_data)
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"Найдено вакансий: {len(result)}")
    
    if result:
        print(f"\n📋 ПЕРВЫЕ 3 ВАКАНСИИ:")
        for i, v in enumerate(result[:3]):
            print(f"\n--- Вакансия {i+1} ---")
            print(f"  Должность: {v['position']}")
            print(f"  Объект: {v['location']}")
            print(f"  Оплата: {v['salary'][:50]}...")
            print(f"  Условия: {v['conditions'][:50]}...")
            print(f"  Требования: {v['requirements'][:50]}...")
            print(f"  Потребность: {v['positions_needed']}")
            print(f"  Менеджер: {v['manager']}")
            print(f"  Компания: {v['company']}")
            print(f"  Преимущества: {v['benefits'][:50]}...")
    
    print(f"\n✅ Тест завершен!")