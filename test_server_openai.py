#!/usr/bin/env python3
"""Тест OpenAI на сервере"""

import requests
import json

def test_server_openai():
    print("🧪 Тестируем OpenAI на сервере...")
    
    # Тест 1: Простой запрос
    response = requests.post(
        'http://72.56.66.228/api/trends/rewrite',
        headers={'Content-Type': 'application/json'},
        json={'transcript': 'Тест простой'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        result = data.get('rewritten_text', '')
        print(f"Result: {result[:100]}...")
        
        # Проверяем что это НЕ демо данные
        if "🔥" in result and "💪" in result and "#вирусный" in result:
            print("❌ ОШИБКА: Получены демо данные!")
            return False
        elif "⚠️ ВНИМАНИЕ" in result:
            print("⚠️ Получено предупреждение об ошибке API")
            return False
        else:
            print("✅ Успех: Получен реальный переписанный текст")
            return True
    else:
        print(f"❌ Ошибка HTTP: {response.text}")
        return False

if __name__ == "__main__":
    success = test_server_openai()
    exit(0 if success else 1)
