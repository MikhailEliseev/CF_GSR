#!/bin/bash

# Скрипт быстрого запуска Контент Завода

echo "🚀 Запуск Контент Завода..."

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Проверка Redis
echo "🔴 Проверка Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis не запущен. Попытка запуска..."
    if command -v redis-server > /dev/null; then
        redis-server --daemonize yes
        sleep 2
    else
        echo "❌ Redis не установлен. Установите Redis и запустите заново."
        exit 1
    fi
fi

# Создание .env если не существует
if [ ! -f ".env" ]; then
    echo "📝 Создание файла .env..."
    cp .env.example .env
    echo "⚠️  Заполните API ключи в файле .env или в веб-интерфейсе"
fi

# Запуск приложения
echo "🎉 Запуск приложения..."
python run.py
