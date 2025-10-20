#!/usr/bin/env python3
"""Тест переписывания текста через OpenAI"""

from api.openai_client import OpenAIClient

def test_openai_rewrite():
    print("🧪 Тестируем переписывание через OpenAI...")
    
    # Создаем клиента с новым ключом
    client = OpenAIClient()
    
    # Тестовый текст
    text = "Ищем работников на стройку. Хорошая зарплата, стабильная работа."
    
    print(f"📝 Исходный текст: {text}")
    
    try:
        # Переписываем текст
        result = client.rewrite_text(text)
        print(f"✅ Результат OpenAI: {result}")
        
        # Проверяем что это НЕ демо данные
        if "🔥" in result and "💪" in result:
            print("❌ ОШИБКА: Получены демо данные!")
            return False
        else:
            print("✅ Успех: Получен реальный переписанный текст")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_rewrite()
    exit(0 if success else 1)
