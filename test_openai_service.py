#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from services.openai_service import OpenAIService

print("🧪 Тестируем OpenAIService.generate_text()...")

service = OpenAIService(api_key="test")
result = service.generate_text("Привет, мир!")
print(f"Результат: {result}")

print("✅ Тест завершен успешно!")
