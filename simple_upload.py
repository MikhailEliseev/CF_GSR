#!/usr/bin/env python3
import requests
import json

# Читаем исправленный файл
with open('deploy_504_fix/module_trends.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Разбиваем на части для загрузки
chunk_size = 10000
chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

print(f"Загружаем {len(chunks)} частей...")

for i, chunk in enumerate(chunks):
    try:
        # Отправляем как JSON
        data = {
            'chunk': i,
            'total': len(chunks),
            'content': chunk
        }
        
        response = requests.post(
            'http://72.56.66.228/api/trends/collect-reels',
            json=data,
            timeout=10
        )
        
        print(f"Часть {i+1}/{len(chunks)}: {response.status_code}")
        
    except Exception as e:
        print(f"Ошибка в части {i+1}: {e}")

print("Загрузка завершена!")
