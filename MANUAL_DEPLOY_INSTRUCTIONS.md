# Инструкции для ручного деплоя изменений HeyGen аватаров

## Проблема
SSH подключение к серверу недоступно, но сервер работает на http://72.56.66.228:5000

## Файлы для обновления

### 1. config.py
**Изменение:** Обновлён API ключ HeyGen
```python
'heygen_api_key': os.getenv('DEFAULT_HEYGEN_API_KEY', 'sk_V2_hgu_k4mPZuZ8zWs_hyLcthEgFcLFgOT7SRGNtPnC9N6Nwt2z'),
```

### 2. app_current_backup.py
**Изменение:** Добавлен новый endpoint для аватаров
```python
@app.route('/api/vacancies/list-avatars', methods=['GET'])
def list_vacancy_avatars():
    """Получение списка доступных аватаров HeyGen для модуля вакансий"""
    # ... код endpoint'а
```

### 3. templates/module_vacancies.html
**Изменения:**
- Обновлён HTML шага 5 с выбором аватара и ориентацией
- Добавлены JavaScript функции loadAvatars() и generateAvatarPreview()
- Обновлена функция generateVideo() для передачи avatar_id и video_format

### 4. routes/vacancies.py
**Изменение:** Обновлена логика генерации видео
```python
# Создаем видео БЕЗ fallback на placeholder
video_id = client.create_video(avatar_id, audio_url, video_format)
```

## Способ обновления

### Вариант 1: Через веб-интерфейс
1. Откройте http://72.56.66.228:5000/settings/vacancies
2. Найдите раздел загрузки файлов
3. Загрузите обновлённые файлы

### Вариант 2: Через SSH (если доступен)
```bash
# Скопируйте файлы на сервер
scp config.py root@72.56.66.228:/var/www/gsr_content_factory/
scp app_current_backup.py root@72.56.66.228:/var/www/gsr_content_factory/
scp templates/module_vacancies.html root@72.56.66.228:/var/www/gsr_content_factory/templates/
scp routes/vacancies.py root@72.56.66.228:/var/www/gsr_content_factory/routes/

# Перезапустите сервер
ssh root@72.56.66.228 "sudo systemctl restart gsr_content_factory"
```

### Вариант 3: Через Timeweb панель
1. Откройте панель управления Timeweb
2. Найдите файловый менеджер
3. Обновите файлы в директории /var/www/gsr_content_factory/
4. Перезапустите сервер

## Тестирование после обновления

1. Проверьте endpoint: http://72.56.66.228:5000/api/vacancies/list-avatars
2. Откройте модуль вакансий: http://72.56.66.228:5000/module/vacancies
3. Проверьте что в шаге 5 загружается список аватаров
4. Проверьте что генерация видео работает без "кролика"

## Ожидаемый результат

- ✅ Список аватаров загружается из HeyGen API
- ✅ Мои аватары (⭐) отображаются вверху списка  
- ✅ При выборе аватара показывается preview
- ✅ Можно выбрать ориентацию: 9:16 или 16:9
- ✅ Генерация видео использует реальный HeyGen API
- ✅ НЕТ fallback на Big Buck Bunny (кролика)