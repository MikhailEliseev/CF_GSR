#!/usr/bin/env python3
"""Тест error fallback когда все API недоступны"""

from api.openai_client import OpenAIClient

def test_error_fallback():
    print("🧪 Тестируем error fallback...")
    
    # Создаем клиента с неправильным ключом и ломаем Gemini
    client = OpenAIClient(api_key="wrong_key")
    client.base_url = "https://invalid.openai.com"  # Ломаем OpenAI
    client._gemini_request = lambda x: exec('raise Exception("Gemini broken")')  # Ломаем Gemini
    
    text = "Тест"
    print(f"📝 Исходный текст: {text}")
    
    try:
        result = client.rewrite_text(text)
        print(f"✅ Результат error fallback: {result}")
        
        # Проверяем что это предупреждение об ошибке
        if "⚠️ ВНИМАНИЕ" in result and "AI сервисы временно недоступны" in result:
            print("✅ Успех: Получено честное предупреждение об ошибке")
            return True
        else:
            print("❌ ОШИБКА: Не получено предупреждение об ошибке!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_error_fallback()
    exit(0 if success else 1)
