#!/usr/bin/env python3
"""
Исправление проблемы с загрузкой CSV файлов
"""

import paramiko
import time

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def fix_csv_upload_issue():
    """Исправляем проблему с загрузкой CSV файлов"""
    print("🔧 Исправляем проблему с загрузкой CSV файлов...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Проверяем текущий файл
        print("\n1️⃣ Проверяем текущий файл...")
        stdin, stdout, stderr = ssh.exec_command("grep -n 'function loadCsv' /root/templates/module_vacancies.html")
        line_info = stdout.read().decode()
        print(f"Найдена функция loadCsv: {line_info}")
        
        # 2. Проверяем есть ли ошибка в функции loadCsv
        print("\n2️⃣ Проверяем функцию loadCsv...")
        stdin, stdout, stderr = ssh.exec_command("sed -n '276,308p' /root/templates/module_vacancies.html")
        function_code = stdout.read().decode()
        print("Код функции loadCsv:")
        print(function_code)
        
        # 3. Проверяем есть ли пустая строка в начале функции
        if function_code.strip().startswith('function loadCsv() {\n    \n    const fileInput'):
            print("❌ Найдена проблема: пустая строка в начале функции")
            
            # Исправляем проблему
            print("\n3️⃣ Исправляем проблему...")
            
            # Создаем исправленную версию функции
            fixed_function = '''// Загрузка CSV файла
function loadCsv() {
    console.log('🔄 Загружаем CSV файл...');
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Выберите CSV файл');
        return;
    }
    
    showStatus('Загружаем CSV...', 'info');
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/vacancies/upload-csv', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus(`✅ Загружено ${data.count} вакансий из CSV`, 'success');
            displayVacancies(data.vacancies);
        } else {
            showStatus('❌ Ошибка: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('❌ Ошибка:', error);
        showStatus('❌ Ошибка: ' + error.message, 'error');
    });
}'''
            
            # Заменяем функцию
            stdin, stdout, stderr = ssh.exec_command("sed -i '276,308c\\" + fixed_function + "' /root/templates/module_vacancies.html")
            stdout.read()
            print("✅ Функция loadCsv исправлена")
        else:
            print("✅ Функция loadCsv выглядит корректно")
        
        # 4. Проверяем что файл обновился
        print("\n4️⃣ Проверяем обновление...")
        stdin, stdout, stderr = ssh.exec_command("grep -A 5 'function loadCsv' /root/templates/module_vacancies.html")
        updated_function = stdout.read().decode()
        print("Обновленная функция:")
        print(updated_function)
        
        # 5. Тестируем загрузку CSV
        print("\n5️⃣ Тестируем загрузку CSV...")
        test_cmd = "curl -X POST -F 'file=@/root/test_data/real_vacancies.csv' http://localhost:5000/api/vacancies/upload-csv"
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        result = stdout.read().decode()
        
        if "success" in result and "count" in result:
            print("✅ CSV загрузка работает!")
            print("🎉 Проблема решена!")
            return True
        else:
            print(f"❌ CSV загрузка не работает: {result[:200]}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    success = fix_csv_upload_issue()
    if success:
        print("\n✅ Проблема с загрузкой CSV файлов решена!")
        print("Теперь можно тестировать на http://72.56.66.228/module/vacancies")
        print("Используйте кнопку 'Загрузить CSV' для загрузки файлов")
    else:
        print("\n❌ Проблема не решена")
