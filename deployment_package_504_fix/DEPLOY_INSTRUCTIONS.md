# 🚀 Инструкции по внедрению исправления 504 ошибки

## 📋 Что исправлено
- ✅ По умолчанию 3 рилса вместо 20
- ✅ Безопасные опции (1, 3, 5, 10 рилсов)
- ✅ Предупреждения для больших значений
- ✅ Правильный параметр API (`count`)

## 🔧 Файлы для замены
1. `templates/module_trends.html` - основной интерфейс
2. `routes/trends.py` - API (уже исправлен)

## 📦 Команды внедрения

### 1. Создать бекап на сервере
```bash
cp /path/to/templates/module_trends.html /path/to/templates/module_trends_backup_$(date +%Y%m%d_%H%M%S).html
```

### 2. Заменить файлы
```bash
# Заменить интерфейс
cp module_trends.html /path/to/templates/

# Проверить права доступа
chmod 644 /path/to/templates/module_trends.html
```

### 3. Перезапустить сервис
```bash
# Перезапустить Flask приложение
sudo systemctl restart your-flask-service
# или
sudo supervisorctl restart your-app
```

## ✅ Проверка внедрения
1. Открыть интерфейс трендвотчинга
2. Проверить, что по умолчанию выбрано "3 рилса"
3. Попробовать собрать рилсы - не должно быть 504 ошибки
4. Проверить, что при выборе 10+ рилсов появляется предупреждение

## 🔄 Откат (если что-то пошло не так)
```bash
cp /path/to/templates/module_trends_backup_YYYYMMDD_HHMMSS.html /path/to/templates/module_trends.html
sudo systemctl restart your-flask-service
```

## 📊 Ожидаемый результат
- ✅ Нет 504 ошибок при сборе 1-5 рилсов
- ✅ Предупреждения для больших значений
- ✅ Стабильная работа интерфейса
