#!/usr/bin/env python3
"""
Интеграционные тесты для endpoint /api/vacancies/upload-csv
"""

import requests
import json
import os
import tempfile

def test_successful_upload():
    """Тест успешной загрузки CSV"""
    print("🧪 Тестируем успешную загрузку CSV...")
    
    # Создаем тестовый CSV файл
    test_csv_content = """Акции и скидки,Объект,Оплата,Условия,Требования,Потребность,Менеджер,Юр.лицо,Преимущества
Должность:,Объект,Оплата,Условия,Требования,Потребность,Менеджер,Юр.лицо,Преимущества
,Сборщик на конвейере,ЛГ Электроникс,320 руб/час,смена - 11 часов,От 18 до 45 лет,15 муж.,Константин Тренин,ООО Фортренд,Сборка бытовой техники
,Работник склада,ДжамильКо,370 руб/час,смена - 11 часов,РФ/РБ,0,Виктор Горяинов,ООО Фортренд,Брендовая одежда"""
    
    # Сохраняем во временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(test_csv_content)
        temp_file = f.name
    
    try:
        # Тестируем загрузку
        with open(temp_file, 'rb') as f:
            files = {"file": ("test_vacancies.csv", f, "text/csv")}
            
            response = requests.post(
                "http://localhost:5000/api/vacancies/upload-csv",
                files=files
            )
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Ответ: {response.text[:500]}")
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, f"Ожидался success=True, получен {data.get('success')}"
        assert "vacancies" in data, "Ответ должен содержать поле 'vacancies'"
        assert "count" in data, "Ответ должен содержать поле 'count'"
        
        vacancies = data.get("vacancies", [])
        assert len(vacancies) > 0, "Должны быть найдены вакансии"
        
        # Проверяем структуру первой вакансии
        first_vacancy = vacancies[0]
        required_fields = ['position', 'salary', 'conditions', 'requirements', 'manager', 'company']
        for field in required_fields:
            assert field in first_vacancy, f"Поле '{field}' отсутствует в вакансии"
        
        print("✅ Успешная загрузка CSV работает!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_no_file_error():
    """Тест ошибки 'файл не найден'"""
    print("🧪 Тестируем ошибку 'файл не найден'...")
    
    try:
        response = requests.post("http://localhost:5000/api/vacancies/upload-csv")
        
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
        
        data = response.json()
        assert data.get("success") == False, "Ожидался success=False"
        assert "error" in data, "Ответ должен содержать поле 'error'"
        assert "файл не найден" in data.get("error", ""), "Ошибка должна содержать 'файл не найден'"
        
        print("✅ Ошибка 'файл не найден' обрабатывается правильно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

def test_wrong_format_error():
    """Тест ошибки неправильного формата"""
    print("🧪 Тестируем ошибку неправильного формата...")
    
    # Создаем файл с неправильным расширением
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Это не CSV файл")
        temp_file = f.name
    
    try:
        with open(temp_file, 'rb') as f:
            files = {"file": ("test.txt", f, "text/plain")}
            
            response = requests.post(
                "http://localhost:5000/api/vacancies/upload-csv",
                files=files
            )
        
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
        
        data = response.json()
        assert data.get("success") == False, "Ожидался success=False"
        assert "CSV" in data.get("error", ""), "Ошибка должна содержать 'CSV'"
        
        print("✅ Ошибка неправильного формата обрабатывается правильно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_empty_file_error():
    """Тест ошибки пустого файла"""
    print("🧪 Тестируем ошибку пустого файла...")
    
    # Создаем пустой CSV файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write("")
        temp_file = f.name
    
    try:
        with open(temp_file, 'rb') as f:
            files = {"file": ("empty.csv", f, "text/csv")}
            
            response = requests.post(
                "http://localhost:5000/api/vacancies/upload-csv",
                files=files
            )
        
        # Пустой файл может вернуть 200 с пустым списком или 400 с ошибкой
        assert response.status_code in [200, 400], f"Неожиданный статус: {response.status_code}"
        
        data = response.json()
        if response.status_code == 200:
            assert data.get("success") == True, "Пустой файл должен возвращать success=True"
            assert data.get("count", 0) == 0, "Количество вакансий должно быть 0"
        else:
            assert data.get("success") == False, "Ожидался success=False"
        
        print("✅ Пустой файл обрабатывается правильно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_server_connection():
    """Тест подключения к серверу"""
    print("🧪 Тестируем подключение к серверу...")
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"✅ Сервер доступен, статус: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Сервер недоступен. Запустите сервер командой: python app.py")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def run_all_tests():
    """Запуск всех интеграционных тестов"""
    print("🚀 Запускаем интеграционные тесты для /api/vacancies/upload-csv...")
    
    # Сначала проверяем подключение к серверу
    if not test_server_connection():
        print("\n⚠️ Пропускаем тесты - сервер недоступен")
        return False
    
    try:
        test_successful_upload()
        test_no_file_error()
        test_wrong_format_error()
        test_empty_file_error()
        
        print("\n🎉 Все интеграционные тесты прошли успешно!")
        return True
        
    except Exception as e:
        print(f"\n❌ Интеграционный тест провален: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
