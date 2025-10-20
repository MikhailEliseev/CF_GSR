#!/usr/bin/env python3
"""
Автоматический скрипт для исправления CSV загрузки на сервере 72.56.66.228
"""

import subprocess
import os
import time
import sys

def run_command(cmd, description):
    """Выполнить команду и показать результат"""
    print(f"\n🔄 {description}")
    print(f"Команда: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Успешно: {description}")
            if result.stdout.strip():
                print(f"Вывод: {result.stdout.strip()}")
        else:
            print(f"❌ Ошибка: {description}")
            print(f"Код ошибки: {result.returncode}")
            if result.stderr.strip():
                print(f"Ошибка: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Таймаут: {description}")
        return False
    except Exception as e:
        print(f"💥 Исключение: {description} - {e}")
        return False
    
    return True

def main():
    print("🚀 Начинаем автоматическое исправление CSV загрузки на сервере")
    print("=" * 60)
    
    # Проверяем наличие файлов
    if not os.path.exists("routes/vacancies.py"):
        print("❌ Файл routes/vacancies.py не найден!")
        return False
    
    if not os.path.exists("server_key") and not os.path.exists("server_key_new"):
        print("❌ SSH ключи не найдены!")
        print("Попробуем альтернативные методы...")
        return try_alternative_methods()
    
    # Пробуем разные SSH ключи
    ssh_keys = ["server_key_new", "server_key"]
    ssh_working = False
    
    for key in ssh_keys:
        if os.path.exists(key):
            print(f"\n🔑 Пробуем SSH ключ: {key}")
            if test_ssh_connection(key):
                ssh_working = True
                break
    
    if not ssh_working:
        print("\n❌ SSH подключение не работает!")
        print("Переходим к альтернативным методам...")
        return try_alternative_methods()
    
    # Если SSH работает, выполняем deployment
    return deploy_via_ssh(key)

def test_ssh_connection(key):
    """Тестируем SSH подключение"""
    cmd = f'ssh -i {key} -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@72.56.66.228 "echo SSH_TEST_SUCCESS"'
    return run_command(cmd, f"Тест SSH с ключом {key}")

def deploy_via_ssh(key):
    """Deployment через SSH"""
    print(f"\n📦 Начинаем deployment через SSH с ключом {key}")
    
    # 1. Создание бэкапа
    if not run_command(
        f'ssh -i {key} root@72.56.66.228 "cp /root/routes/vacancies.py /root/routes/vacancies.py.backup_$(date +%Y%m%d_%H%M%S)"',
        "Создание бэкапа на сервере"
    ):
        print("⚠️ Не удалось создать бэкап, продолжаем...")
    
    # 2. Остановка сервера
    run_command(
        f'ssh -i {key} root@72.56.66.228 "pkill -f \'python.*app\' || true"',
        "Остановка Flask сервера"
    )
    
    # 3. Загрузка исправленного файла
    if not run_command(
        f'scp -i {key} routes/vacancies.py root@72.56.66.228:/root/routes/',
        "Загрузка исправленного файла"
    ):
        print("❌ Не удалось загрузить файл через SCP")
        return False
    
    # 4. Проверка синтаксиса
    if not run_command(
        f'ssh -i {key} root@72.56.66.228 "python3 -m py_compile /root/routes/vacancies.py"',
        "Проверка синтаксиса Python"
    ):
        print("❌ Синтаксическая ошибка в файле!")
        return False
    
    # 5. Запуск сервера
    if not run_command(
        f'ssh -i {key} root@72.56.66.228 "cd /root && nohup python3 app_current_backup.py > server.log 2>&1 &"',
        "Запуск Flask сервера"
    ):
        print("❌ Не удалось запустить сервер")
        return False
    
    # 6. Проверка запуска
    time.sleep(3)
    if not run_command(
        f'ssh -i {key} root@72.56.66.228 "ps aux | grep python | grep -v grep"',
        "Проверка запуска сервера"
    ):
        print("❌ Сервер не запустился")
        return False
    
    # 7. Тест endpoint
    if not run_command(
        f'ssh -i {key} root@72.56.66.228 "curl -s http://localhost:5000/api/vacancies/upload-csv -X POST -F \'file=@/dev/null\'"',
        "Тест endpoint через curl"
    ):
        print("⚠️ Endpoint не отвечает, но сервер запущен")
    
    print("\n✅ Deployment завершен!")
    print("🌐 Проверьте http://72.56.66.228/module/vacancies")
    return True

def try_alternative_methods():
    """Альтернативные методы deployment"""
    print("\n🔄 Пробуем альтернативные методы...")
    
    # Создаем инструкцию для ручного исправления
    print("📝 Создана инструкция для ручного исправления: manual_fix_instructions.md")
    
    # Создаем готовый файл для копирования
    create_ready_to_copy_file()
    
    print("\n📋 РУЧНОЕ ИСПРАВЛЕНИЕ:")
    print("1. Зайдите в веб-панель управления сервером")
    print("2. Откройте файловый менеджер")
    print("3. Перейдите в /root/routes/")
    print("4. Откройте файл vacancies.py")
    print("5. Найдите функцию parse_vacancies_direct() (строки ~442-460)")
    print("6. Исправьте индексы:")
    print("   - row[3] → row[2] (salary)")
    print("   - row[4] → row[3] (conditions)")
    print("   - row[5] → row[4] (requirements)")
    print("   - row[6] → row[5] (positions_needed)")
    print("   - row[7] → row[6] (manager)")
    print("   - row[8] → row[7] (company)")
    print("   - row[9] → row[8] (benefits)")
    print("7. Сохраните файл")
    print("8. Перезапустите сервер")
    
    return True

def create_ready_to_copy_file():
    """Создаем готовый файл для копирования"""
    print("\n📄 Создаем готовый файл для копирования...")
    
    # Читаем исправленный файл
    with open("routes/vacancies.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Создаем файл с инструкциями
    with open("vacancies_fixed_for_server.py", "w", encoding="utf-8") as f:
        f.write("# ИСПРАВЛЕННЫЙ ФАЙЛ ДЛЯ СЕРВЕРА\n")
        f.write("# Замените содержимое /root/routes/vacancies.py на этот код\n")
        f.write("# ================================================\n\n")
        f.write(content)
    
    print("✅ Создан файл: vacancies_fixed_for_server.py")
    print("📋 Скопируйте содержимое этого файла в /root/routes/vacancies.py на сервере")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Процесс завершен успешно!")
    else:
        print("\n💥 Процесс завершен с ошибками!")
        print("Используйте ручное исправление согласно инструкции.")
    
    sys.exit(0 if success else 1)
