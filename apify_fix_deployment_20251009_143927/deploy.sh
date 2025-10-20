#!/bin/bash
# Скрипт развертывания исправления Apify

echo "🚀 Развертывание исправления Apify на сервере"
echo "=============================================="

# Проверяем подключение к серверу
echo "1. Проверка подключения к серверу..."
if ! ssh -i server_key root@72.56.66.228 "echo 'Подключение успешно'"; then
    echo "❌ Ошибка подключения к серверу"
    exit 1
fi

# Создаем backup текущего файла
echo "2. Создание backup текущего файла..."
ssh -i server_key root@72.56.66.228 "
    if [ -f /root/gsr/api/apify_client.py ]; then
        cp /root/gsr/api/apify_client.py /root/gsr/api/apify_client_backup_$(date +%Y%m%d_%H%M%S).py
        echo '✅ Backup создан'
    else
        echo '⚠️ Исходный файл не найден'
    fi
"

# Загружаем исправленный файл
echo "3. Загрузка исправленного файла..."
scp -i server_key apify_client.py root@72.56.66.228:/root/gsr/api/apify_client.py

if [ $? -eq 0 ]; then
    echo "✅ Файл загружен успешно"
else
    echo "❌ Ошибка загрузки файла"
    exit 1
fi

# Проверяем права доступа
echo "4. Проверка прав доступа..."
ssh -i server_key root@72.56.66.228 "
    chmod 644 /root/gsr/api/apify_client.py
    echo '✅ Права доступа установлены'
"

# Перезапускаем приложение
echo "5. Перезапуск приложения..."
ssh -i server_key root@72.56.66.228 "
    cd /root/gsr
    pkill -f 'python.*app_current_backup.py' || true
    sleep 2
    nohup python3 app_current_backup.py > app.log 2>&1 &
    sleep 3
    echo '✅ Приложение перезапущено'
"

# Проверяем статус
echo "6. Проверка статуса приложения..."
ssh -i server_key root@72.56.66.228 "
    if pgrep -f 'python.*app_current_backup.py' > /dev/null; then
        echo '✅ Приложение запущено'
    else
        echo '❌ Приложение не запущено'
        exit 1
    fi
"

echo "🎉 Развертывание завершено успешно!"
echo "🌐 Проверьте: http://72.56.66.228/module/trends"
