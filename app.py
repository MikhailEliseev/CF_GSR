#!/usr/bin/env python3
"""Thin wrapper around the full Content Factory application."""

from app import create_app as _create_core_app


def create_app():
    """Expose the core create_app returning (app, socketio)."""
    return _create_core_app()


if __name__ == "__main__":
    app, socketio = create_app()
    print("🚀 Контент Завод запускается через app.py")
    try:
        socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)
    except OSError:
        print("⚠️ Порт 5000 недоступен, пробуем 5001")
        socketio.run(app, host="0.0.0.0", port=5001, debug=False, allow_unsafe_werkzeug=True)
