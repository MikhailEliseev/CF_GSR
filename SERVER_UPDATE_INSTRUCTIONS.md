# 🔧 Инструкция по обновлению сервера 72.56.66.228

## 📋 Что нужно исправить на сервере:

### ❌ Текущие проблемы:
- API endpoint `/api/settings/<module_name>` возвращает "405 Method Not Allowed"
- API endpoint `/api/competitors` отсутствует
- Ошибки в логах: "Не удалось проверить Apify ключ" и "Ошибка загрузки конкурентов"

### ✅ Что нужно добавить:

1. **GET endpoint для настроек:**
```python
@app.route('/api/settings/<module_name>', methods=['GET', 'POST'])
def manage_settings(module_name):
    if request.method == 'GET':
        # Возвращает настройки в JSON формате
```

2. **GET endpoint для конкурентов:**
```python
@app.route('/api/competitors')
def get_competitors():
    # Возвращает список конкурентов
```

3. **Правильная маршрутизация модулей:**
```python
template_map = {
    'trends': 'module_trends_new.html',
    'vacancies': 'module_vacancies.html', 
    'experts': 'module_experts.html',
    'monitoring': 'module_monitoring.html'
}
```

## 🚀 Способы обновления:

### Вариант 1: SSH доступ
```bash
# Подключиться к серверу
ssh -i ~/.ssh/gsr_server_key root@72.56.66.228

# Заменить файл app.py
cp app_fixed_for_server.py app.py

# Перезапустить приложение
systemctl restart your-app-service
# или
pkill -f "python.*app.py" && python3 app.py &
```

### Вариант 2: Веб-интерфейс хостинга
1. Зайти в панель управления хостингом
2. Открыть файловый менеджер
3. Найти файл `app.py`
4. Заменить содержимое на код из `app_fixed_for_server.py`
5. Перезапустить приложение

### Вариант 3: Git (если используется)
```bash
# На сервере
git pull origin main
# или
git pull origin master
```

### Вариант 4: FTP/SFTP
```bash
# Загрузить файл app_fixed_for_server.py на сервер
# Переименовать в app.py
# Перезапустить приложение
```

## 🔍 Проверка после обновления:

```bash
# Проверить API endpoints
curl http://72.56.66.228/api/settings/trends
curl http://72.56.66.228/api/competitors

# Проверить модули
curl http://72.56.66.228/module/vacancies | grep title
curl http://72.56.66.228/module/experts | grep title
```

## 📁 Файлы для обновления:

- **app_fixed_for_server.py** - исправленная версия app.py
- Все остальные файлы остаются без изменений

## ⚠️ Важно:

1. **Сделайте резервную копию** текущего app.py перед заменой
2. **Перезапустите приложение** после обновления
3. **Проверьте логи** на наличие ошибок
4. **Протестируйте** все модули в браузере

## 🎯 Ожидаемый результат:

После обновления:
- ✅ API endpoints будут работать
- ✅ Ошибки в логах исчезнут  
- ✅ Все модули будут показывать правильные заголовки
- ✅ Проверка Apify ключа будет работать
- ✅ Список конкурентов будет загружаться
