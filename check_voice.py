#!/usr/bin/env python3
import sqlite3
import json

# Подключение к базе данных
conn = sqlite3.connect("gsr_content_factory.db")
cursor = conn.cursor()

# Получение текущих настроек
cursor.execute("SELECT settings_data FROM settings WHERE module_name = 'vacancies'")
result = cursor.fetchone()

if result:
    settings = json.loads(result[0])
    print("🔍 Текущие настройки:")
    print(f"Voice ID: {settings.get('default_voice_id', 'НЕ НАЙДЕН')}")
    print(f"Model: {settings.get('default_voice_model', 'НЕ НАЙДЕН')}")
    print(f"Additional: {settings.get('additional_settings', {})}")
    
    # Проверяем additional_settings
    additional = settings.get('additional_settings', {})
    print(f"Additional Voice ID: {additional.get('default_voice_id', 'НЕ НАЙДЕН')}")
    print(f"Additional Model: {additional.get('default_voice_model', 'НЕ НАЙДЕН')}")
else:
    print("❌ Настройки не найдены")

conn.close()
