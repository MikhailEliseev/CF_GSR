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
    # Парсинг JSON
    settings = json.loads(result[0])
    
    # Обновление голоса
    settings["default_voice_id"] = "21m00Tcm4TlvDq8ikWAM"
    settings["default_voice_model"] = "eleven_monolingual_v1"
    
    # Сохранение в базу
    cursor.execute("UPDATE settings SET settings_data = ? WHERE module_name = 'vacancies'", (json.dumps(settings),))
    conn.commit()
    
    print("✅ Голос обновлен на 21m00Tcm4TlvDq8ikWAM")
    print(f"📝 Новые настройки: {json.dumps(settings, indent=2)}")
else:
    print("❌ Настройки не найдены")

conn.close()
