#!/usr/bin/env python3
"""
Скрипт для обновления файлов на сервере через HTTP
"""

import requests
import json
import base64

def update_file_on_server(file_path, content, server_url="http://72.56.66.228:5000"):
    """Обновляет файл на сервере через HTTP API"""
    try:
        # Кодируем содержимое файла в base64
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # Отправляем запрос на обновление
        response = requests.post(f"{server_url}/api/update-file", 
                                json={
                                    'file_path': file_path,
                                    'content': content_b64
                                },
                                timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Файл {file_path} обновлён успешно")
            return True
        else:
            print(f"❌ Ошибка обновления {file_path}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при обновлении {file_path}: {e}")
        return False

def main():
    """Основная функция обновления"""
    print("🚀 Начинаем обновление файлов на сервере...")
    
    # Читаем файлы для обновления
    files_to_update = [
        ('config.py', 'config.py'),
        ('app_current_backup.py', 'app_current_backup.py'),
        ('templates/module_vacancies.html', 'templates/module_vacancies.html'),
        ('routes/vacancies.py', 'routes/vacancies.py')
    ]
    
    success_count = 0
    
    for local_path, server_path in files_to_update:
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if update_file_on_server(server_path, content):
                success_count += 1
                
        except Exception as e:
            print(f"❌ Ошибка чтения файла {local_path}: {e}")
    
    print(f"\n📊 Результат: {success_count}/{len(files_to_update)} файлов обновлено")
    
    if success_count == len(files_to_update):
        print("✅ Все файлы обновлены успешно!")
        print("🔄 Перезапускаем сервер...")
        
        # Попытка перезапуска сервера
        try:
            response = requests.post("http://72.56.66.228:5000/api/restart", timeout=10)
            if response.status_code == 200:
                print("✅ Сервер перезапущен")
            else:
                print("⚠️ Не удалось перезапустить сервер автоматически")
        except:
            print("⚠️ Не удалось перезапустить сервер автоматически")
    else:
        print("❌ Некоторые файлы не удалось обновить")

if __name__ == "__main__":
    main()
