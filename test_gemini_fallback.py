#!/usr/bin/env python3
"""Тест Gemini fallback"""

from api.openai_client import OpenAIClient

def test_gemini_fallback():
    print("🧪 Тестируем Gemini fallback...")
    
    # Создаем клиента БЕЗ ключа OpenAI
    client = OpenAIClient(api_key=None)
    
    text = "Ищем работников на стройку. Хорошая зарплата."
    print(f"📝 Исходный текст: {text}")
    
    try:
        result = client.rewrite_text(text)
        print(f"✅ Результат Gemini: {result}")
        
        # Проверяем что это НЕ демо данные
        if "🔥" in result and "💪" in result and "#вирусный" in result:
            print("❌ ОШИБКА: Получены демо данные!")
            return False
        else:
            print("✅ Успех: Получен реальный переписанный текст от Gemini")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_fallback()
    exit(0 if success else 1)
