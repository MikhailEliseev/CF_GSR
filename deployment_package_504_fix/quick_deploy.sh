#!/bin/bash
# 🚀 Быстрое внедрение исправления 504 ошибки

echo "🔧 Начинаем внедрение исправления 504 ошибки..."

# Создаем бекап
echo "📦 Создаем бекап..."
cp /path/to/templates/module_trends.html /path/to/templates/module_trends_backup_$(date +%Y%m%d_%H%M%S).html

# Заменяем файлы
echo "🔄 Заменяем файлы..."
cp module_trends.html /path/to/templates/
chmod 644 /path/to/templates/module_trends.html

# Перезапускаем сервис
echo "🔄 Перезапускаем сервис..."
# sudo systemctl restart your-flask-service
# или
# sudo supervisorctl restart your-app

echo "✅ Внедрение завершено!"
echo "🧪 Проверьте интерфейс - по умолчанию должно быть 3 рилса"
echo "📊 Попробуйте собрать рилсы - не должно быть 504 ошибки"
