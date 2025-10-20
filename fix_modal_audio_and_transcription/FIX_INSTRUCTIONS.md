# 🔧 Исправление двух проблем

## 🎵 ПРОБЛЕМА #1: Аудио продолжает играть после закрытия модального окна

### ✅ ИСПРАВЛЕНО:
- Добавлен обработчик `hidden.bs.modal` для остановки видео
- Видео останавливается и сбрасывается в начало при закрытии модального окна

### 📝 Изменения в `templates/module_trends.html`:
```javascript
// Добавляем обработчик закрытия модального окна для остановки видео
modal._element.addEventListener('hidden.bs.modal', function() {
    console.log('🔇 Останавливаем видео при закрытии модального окна');
    const video = document.querySelector('#reelPreviewModal video');
    if (video) {
        video.pause();
        video.currentTime = 0;
    }
});
```

## 🎤 ПРОБЛЕМА #2: Ошибка транскрибации HTTP 504 Gateway Time-out

### ✅ ИСПРАВЛЕНО:
- Увеличен таймаут с 60 секунд до 5 минут (300 секунд)
- Добавлена обработка ошибок в API
- Улучшено логирование процесса транскрибации

### 📝 Изменения в `api/assemblyai_client.py`:
```python
timeout = 300  # 5 минут для длинных видео (было 60)
```

### 📝 Изменения в `routes/trends.py`:
```python
@trends_bp.route('/api/trends/transcribe', methods=['POST'])
def transcribe_reel():
    """Транскрибация видео через AssemblyAI с увеличенным таймаутом"""
    try:
        # ... транскрибация с обработкой ошибок
        return jsonify({'success': True, 'transcript': transcript})
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Ошибка транскрибации: {str(e)}. Попробуйте еще раз или проверьте URL видео.'
        }), 500
```

## 🚀 Команды внедрения:

### 1. Создать бекап
```bash
cp /path/to/templates/module_trends.html /path/to/templates/module_trends_backup_$(date +%Y%m%d_%H%M%S).html
cp /path/to/routes/trends.py /path/to/routes/trends_backup_$(date +%Y%m%d_%H%M%S).py
cp /path/to/api/assemblyai_client.py /path/to/api/assemblyai_client_backup_$(date +%Y%m%d_%H%M%S).py
```

### 2. Заменить файлы
```bash
cp module_trends.html /path/to/templates/
cp trends.py /path/to/routes/
cp assemblyai_client.py /path/to/api/
```

### 3. Перезапустить сервис
```bash
sudo systemctl restart your-flask-service
```

## ✅ Ожидаемый результат:
- ✅ Аудио останавливается при закрытии модального окна
- ✅ Транскрибация работает без 504 ошибки
- ✅ Увеличенный таймаут для длинных видео
- ✅ Улучшенная обработка ошибок

## 🔄 Откат (если что-то пошло не так):
```bash
cp /path/to/templates/module_trends_backup_YYYYMMDD_HHMMSS.html /path/to/templates/module_trends.html
cp /path/to/routes/trends_backup_YYYYMMDD_HHMMSS.py /path/to/routes/trends.py
cp /path/to/api/assemblyai_client_backup_YYYYMMDD_HHMMSS.py /path/to/api/assemblyai_client.py
sudo systemctl restart your-flask-service
```
