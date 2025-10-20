#!/usr/bin/env python3
"""Entry point for the refactored Content Factory application."""

from app import create_app


if __name__ == "__main__":
    app, socketio = create_app()
    print("🚀 Контент Завод запускается в обновленном режиме")
    try:
        socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)
    except OSError:
        print("⚠️ Порт 5000 недоступен, пробуем 5001")
        socketio.run(app, host="0.0.0.0", port=5001, debug=False, allow_unsafe_werkzeug=True)
