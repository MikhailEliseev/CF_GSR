# Инструкция для ручного исправления CSV загрузки на сервере

## Проблема
На сервере 72.56.66.228 модуль вакансий возвращает ошибку "Unexpected token '<'" при загрузке CSV файлов.

## Причина
В файле `/root/routes/vacancies.py` неправильные индексы колонок в функции `parse_vacancies_direct()`.

## Решение

### Шаг 1: Подключение к серверу
1. Зайти в веб-панель управления сервером (Timeweb, VPS панель)
2. Открыть файловый менеджер
3. Перейти в папку `/root/routes/`
4. Найти файл `vacancies.py`

### Шаг 2: Создание бэкапа
1. Скопировать файл `vacancies.py` в `vacancies.py.backup_before_fix`
2. Сохранить копию на случай отката

### Шаг 3: Исправление индексов колонок
Найти функцию `parse_vacancies_direct()` (примерно строки 442-460) и исправить:

**БЫЛО (неправильно):**
```python
vacancies.append({
    'position': row[1].strip() if len(row) > 1 else '',  # Колонка B - Объект (должность)
    'location': row[1].strip() if len(row) > 1 else '',  # Колонка B - Объект
    'salary': row[3].strip() if len(row) > 3 else '',    # Колонка D - Оплата
    'conditions': row[4].strip() if len(row) > 4 else '', # Колонка E - Условия
    'requirements': row[5].strip() if len(row) > 5 else '', # Колонка F - Требования
    'positions_needed': row[6].strip() if len(row) > 6 else '', # Колонка G - Потребность
    'manager': row[7].strip() if len(row) > 7 else '',   # Колонка H - Менеджер
    'company': row[8].strip() if len(row) > 8 else '',   # Колонка I - Юр.лицо
    'benefits': row[9].strip() if len(row) > 9 else ''   # Колонка J - Преимущества
})
```

**ДОЛЖНО БЫТЬ (правильно):**
```python
vacancies.append({
    'position': row[1].strip() if len(row) > 1 else '',  # Колонка B - Объект (должность)
    'location': row[1].strip() if len(row) > 1 else '',  # Колонка B - Объект
    'salary': row[2].strip() if len(row) > 2 else '',    # ✅ Колонка C - Оплата (ИСПРАВЛЕНО)
    'conditions': row[3].strip() if len(row) > 3 else '', # ✅ Колонка D - Условия (ИСПРАВЛЕНО)
    'requirements': row[4].strip() if len(row) > 4 else '', # ✅ Колонка E - Требования (ИСПРАВЛЕНО)
    'positions_needed': row[5].strip() if len(row) > 5 else '', # ✅ Колонка F - Потребность (ИСПРАВЛЕНО)
    'manager': row[6].strip() if len(row) > 6 else '',   # ✅ Колонка G - Менеджер (ИСПРАВЛЕНО)
    'company': row[7].strip() if len(row) > 7 else '',   # ✅ Колонка H - Юр.лицо (ИСПРАВЛЕНО)
    'benefits': row[8].strip() if len(row) > 8 else ''    # ✅ Колонка I - Преимущества (ИСПРАВЛЕНО)
})
```

### Шаг 4: Исправление circular import
Найти строку (примерно строка 6):
```python
from app_current_backup import db
```

Заменить на:
```python
# ИСПРАВЛЕНО: Убираем circular import
# from app_current_backup import db
```

### Шаг 5: Сохранение файла
1. Сохранить изменения
2. Проверить, что файл сохранился корректно

### Шаг 6: Перезапуск сервера
1. В веб-панели найти раздел "Процессы" или "Сервисы"
2. Найти процесс Python/Flask
3. Остановить процесс
4. Запустить заново командой:
   ```bash
   cd /root && nohup python3 app_current_backup.py > server.log 2>&1 &
   ```

### Шаг 7: Проверка работы
1. Открыть http://72.56.66.228/module/vacancies
2. Загрузить тестовый CSV файл
3. Проверить, что данные отображаются правильно
4. Убедиться, что salary содержит зарплату (не название компании)

## Альтернативный способ (через SSH)

Если SSH все-таки заработает:

```bash
# 1. Создать бэкап
ssh root@72.56.66.228 "cp /root/routes/vacancies.py /root/routes/vacancies.py.backup_before_fix"

# 2. Остановить сервер
ssh root@72.56.66.228 "pkill -f 'python.*app' || true"

# 3. Загрузить исправленный файл
scp -i server_key routes/vacancies.py root@72.56.66.228:/root/routes/

# 4. Проверить синтаксис
ssh root@72.56.66.228 "python3 -m py_compile /root/routes/vacancies.py"

# 5. Запустить сервер
ssh root@72.56.66.228 "cd /root && nohup python3 app_current_backup.py > server.log 2>&1 &"

# 6. Проверить, что запустился
ssh root@72.56.66.228 "ps aux | grep python | grep -v grep"
```

## Проверка результата

После исправления:
1. CSV файлы должны загружаться без ошибок
2. Все поля должны заполняться правильными данными
3. Salary должно содержать зарплату, а не название компании
4. В логах не должно быть ERROR

## Откат (если что-то пошло не так)

```bash
# Восстановить бэкап
ssh root@72.56.66.228 "cp /root/routes/vacancies.py.backup_before_fix /root/routes/vacancies.py"
# Перезапустить сервер
ssh root@72.56.66.228 "pkill -f python && cd /root && nohup python3 app_current_backup.py > server.log 2>&1 &"
```
