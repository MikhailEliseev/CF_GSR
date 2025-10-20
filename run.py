#!/usr/bin/env python3
"""
Скрипт для запуска Контент Завода
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_redis():
    """Проверка доступности Redis"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return True
    except Exception:
        return False

def start_redis():
    """Запуск Redis (если установлен)"""
    try:
        subprocess.Popen(['redis-server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        return check_redis()
    except FileNotFoundError:
        print("❌ Redis не найден. Установите Redis:")
        print("   Ubuntu/Debian: sudo apt-get install redis-server")
        print("   macOS: brew install redis")
        print("   Windows: https://redis.io/download")
        return False

def start_celery():
    """Запуск Celery worker"""
    try:
        celery_process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'celery_app', 'worker', '--loglevel=info'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return celery_process
    except FileNotFoundError:
        print("❌ Celery не найден. Установите: pip install celery")
        return None

def check_dependencies():
    """Проверка зависимостей"""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_socketio', 
        'celery', 'redis', 'requests', 'openai'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Отсутствуют зависимости: {', '.join(missing)}")
        print("Установите их командой: pip install -r requirements.txt")
        return False
    
    return True

def setup_database():
    """Инициализация базы данных"""
    try:
        from app import create_app
        from models import db
        
        app, _ = create_app()
        with app.app_context():
            db.create_all()
            print("✅ База данных инициализирована")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return False

def main():
    print("🚀 Запуск Контент Завода...")
    print("=" * 50)

    # Обновляем PATH, чтобы использовать бинарники текущего виртуального окружения
    venv_bin = Path(sys.executable).resolve().parent
    current_path = os.environ.get('PATH', '')
    path_parts = [str(venv_bin)] + [p for p in current_path.split(os.pathsep) if p]
    os.environ['PATH'] = os.pathsep.join(path_parts)

    # Проверка зависимостей
    print("🔍 Проверка зависимостей...")
    if not check_dependencies():
        sys.exit(1)
    
    # Инициализация БД
    print("🗄️  Инициализация базы данных...")
    if not setup_database():
        sys.exit(1)
    
    # Проверка Redis
    print("🔴 Проверка Redis...")
    if not check_redis():
        print("⚠️  Redis не запущен. Попытка запуска...")
        if not start_redis():
            print("❌ Не удалось запустить Redis")
            sys.exit(1)
    print("✅ Redis доступен")
    
    # Запуск Celery
    print("⚙️  Запуск Celery worker...")
    celery_process = start_celery()
    if not celery_process:
        sys.exit(1)
    print("✅ Celery worker запущен")
    
    # Запуск Flask приложения
    print("🌐 Запуск веб-сервера...")
    try:
        from app import create_app
        app, socketio = create_app()
        
        print("=" * 50)
        print("🎉 Контент Завод запущен!")
        print("📱 Веб-интерфейс: http://localhost:5000")
        print("⚠️  Для остановки нажмите Ctrl+C")
        print("=" * 50)
        
        # Запускать только через этот файл или start.sh!
        # Использует app.py (который теперь thin-обертка над app_current_backup.py)
        socketio.run(app, debug=False, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
        if celery_process:
            celery_process.terminate()
        print("✅ Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        if celery_process:
            celery_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    # Переходим в директорию скрипта
    os.chdir(Path(__file__).parent)
    main()
