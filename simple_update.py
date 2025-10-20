#!/usr/bin/env python3
"""
Простое обновление сервера через веб-интерфейс
"""

import subprocess
import time
import requests
import os

def check_server_status():
    """Проверяет статус сервера"""
    print("🔍 Проверяю статус сервера...")
    try:
        response = requests.get("http://72.56.66.228", timeout=10)
        print(f"📊 Статус: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def create_upload_instructions():
    """Создает инструкции для загрузки"""
    print("📋 Создаю инструкции для загрузки...")
    
    instructions = """# 🚀 ИНСТРУКЦИИ ПО ОБНОВЛЕНИЮ СЕРВЕРА

## 📁 ГОТОВЫЕ ФАЙЛЫ:
- ✅ app_for_server_final.py - ВЕРСИЯ БЕЗ ДЕМО ДАННЫХ
- ✅ server_key.pub - ПУБЛИЧНЫЙ SSH КЛЮЧ
- ✅ server_key - ПРИВАТНЫЙ SSH КЛЮЧ

## 🔧 СПОСОБЫ ОБНОВЛЕНИЯ:

### 1️⃣ ЧЕРЕЗ ВЕБ-ПАНЕЛЬ ХОСТИНГА:
1. Войдите в панель управления хостингом
2. Откройте файловый менеджер
3. Найдите файл app.py
4. Создайте резервную копию: app_backup.py
5. Загрузите app_for_server_final.py
6. Переименуйте в app.py
7. Запустите приложение через терминал

### 2️⃣ ЧЕРЕЗ SSH (после добавления ключа):
```bash
# Добавьте публичный ключ в панель управления
# Затем выполните:

# Загрузите файл
scp -i server_key app_for_server_final.py user@72.56.66.228:/tmp/

# Подключитесь к серверу
ssh -i server_key user@72.56.66.228

# Найдите папку с приложением
find / -name "app.py" 2>/dev/null

# Перейдите в папку
cd /path/to/your/app

# Остановите процессы
pkill -f python

# Замените файл
cp /tmp/app_for_server_final.py app.py

# Запустите приложение
python3 app.py
```

### 3️⃣ ЧЕРЕЗ FTP/SFTP:
1. Откройте FTP клиент
2. Подключитесь к 72.56.66.228
3. Найдите папку с приложением
4. Загрузите app_for_server_final.py
5. Переименуйте в app.py
6. Запустите приложение

## 🔍 ПРОВЕРКА ПОСЛЕ ОБНОВЛЕНИЯ:
1. Откройте http://72.56.66.228/module/trends
2. Нажмите "Собрать рилсы конкурентов"
3. Убедитесь, что НЕТ демо данных

## ⚠️ ВАЖНО:
- Убедитесь, что файл app.py заменен
- Проверьте, что приложение запущено
- Проверьте логи: tail -f app.log
"""
    
    with open("UPLOAD_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    
    print("✅ Инструкции созданы: UPLOAD_INSTRUCTIONS.md")

def create_simple_web_server():
    """Создает простой веб-сервер для скачивания файлов"""
    print("🌐 Запускаю веб-сервер для скачивания файлов...")
    
    try:
        # Запускаем HTTP сервер
        subprocess.Popen(["python3", "-m", "http.server", "8080"], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ Веб-сервер запущен на порту 8080")
        print("🌐 Откройте: http://localhost:8080")
        print("📥 Скачайте файлы для обновления сервера")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return False

def main():
    print("🚀 ПРОСТОЕ ОБНОВЛЕНИЕ СЕРВЕРА")
    print("="*50)
    
    # Проверяем статус
    status = check_server_status()
    if status == 200:
        print("✅ Сервер работает!")
    elif status == 502:
        print("❌ Сервер не запущен (502 Bad Gateway)")
    else:
        print(f"⚠️ Статус: {status}")
    
    # Создаем инструкции
    create_upload_instructions()
    
    # Запускаем веб-сервер
    create_simple_web_server()
    
    print("\n" + "="*50)
    print("📋 ГОТОВЫЕ ФАЙЛЫ:")
    print("✅ app_for_server_final.py - ВЕРСИЯ БЕЗ ДЕМО ДАННЫХ")
    print("✅ server_key.pub - ПУБЛИЧНЫЙ SSH КЛЮЧ")
    print("✅ server_key - ПРИВАТНЫЙ SSH КЛЮЧ")
    print("✅ UPLOAD_INSTRUCTIONS.md - ИНСТРУКЦИИ")
    
    print("\n🌐 ВЕБ-СЕРВЕР: http://localhost:8080")
    print("📥 Скачайте файлы и обновите сервер")
    
    print("\n🔧 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Скачайте app_for_server_final.py")
    print("2. Загрузите на сервер через панель управления")
    print("3. Замените app.py на сервере")
    print("4. Запустите приложение")
    print("5. Проверьте результат")

if __name__ == "__main__":
    main()
