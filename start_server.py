#!/usr/bin/env python3
"""Простой скрипт для запуска сервера"""

import sys
sys.path.append('.')

from app import create_app

if __name__ == "__main__":
    app, socketio = create_app()
    print("✅ App создан с исправленными настройками шаблонов")
    print("🚀 Запускаем сервер на порту 5001...")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
