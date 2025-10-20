
# ИНСТРУКЦИИ ПО РАЗВЕРТЫВАНИЮ ИСПРАВЛЕННОЙ ВЕРСИИ
# Создано: 2025-10-05 12:10:10

## ТЕКУЩЕЕ СОСТОЯНИЕ
- Сервер: 72.56.66.228
- Статус: 502 Bad Gateway (приложение не запущено)
- Архив готов: gsr_deploy_20251003_165241.tar.gz

## СПОСОБ 1: ЧЕРЕЗ SSH (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Подключение к серверу
```bash
ssh -i server_key root@72.56.66.228
```

### Шаг 2: Остановка текущего приложения
```bash
# Остановить все процессы Python
pkill -f python
pkill -f gunicorn
pkill -f uwsgi

# Остановить nginx (если нужно)
systemctl stop nginx
```

### Шаг 3: Создание резервной копии
```bash
# Создать папку для бэкапа
mkdir -p /root/backup_20251005_121010

# Скопировать текущие файлы
cp -r /var/www/html/* /root/backup_20251005_121010/ 2>/dev/null || true
cp -r /home/ubuntu/* /root/backup_20251005_121010/ 2>/dev/null || true
```

### Шаг 4: Загрузка нового архива
```bash
# Создать рабочую директорию
mkdir -p /var/www/gsr_new
cd /var/www/gsr_new

# Загрузить архив (нужно скопировать файл на сервер)
# Если у вас есть доступ к веб-панели, загрузите gsr_deploy_20251003_165241.tar.gz
```

### Шаг 5: Распаковка и настройка
```bash
# Распаковать архив
tar -xzf gsr_deploy_20251003_165241.tar.gz

# Установить зависимости
pip3 install -r requirements.txt

# Создать директории
mkdir -p uploads
mkdir -p static/audio
mkdir -p logs

# Установить права
chmod +x app_for_server_final.py
chmod 755 uploads
chmod 755 static
```

### Шаг 6: Настройка базы данных
```bash
# Инициализировать базу данных
python3 -c "
from app_for_server_final import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('База данных инициализирована')
"
```

### Шаг 7: Запуск приложения
```bash
# Запустить приложение
python3 app_for_server_final.py

# Или в фоновом режиме
nohup python3 app_for_server_final.py > app.log 2>&1 &
```

### Шаг 8: Настройка nginx
```bash
# Создать конфигурацию nginx
cat > /etc/nginx/sites-available/gsr << 'EOF'
server {
    listen 80;
    server_name 72.56.66.228;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /var/www/gsr_new/static;
    }
}
EOF

# Активировать конфигурацию
ln -sf /etc/nginx/sites-available/gsr /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверить конфигурацию
nginx -t

# Перезапустить nginx
systemctl restart nginx
```

## СПОСОБ 2: ЧЕРЕЗ ВЕБ-ПАНЕЛЬ ХОСТИНГА

### Если у вас есть доступ к панели управления:

1. **Загрузить архив**: Загрузите файл `gsr_deploy_20251003_165241.tar.gz` через файловый менеджер
2. **Распаковать**: Распакуйте архив в корневую директорию сайта
3. **Установить зависимости**: Выполните `pip3 install -r requirements.txt`
4. **Настроить базу данных**: Запустите инициализацию БД
5. **Настроить веб-сервер**: Укажите `app_for_server_final.py` как точку входа

## ПРОВЕРКА РАЗВЕРТЫВАНИЯ

После развертывания проверьте:

1. **Основная страница**: http://72.56.66.228/
2. **API endpoints**: 
   - http://72.56.66.228/api/trends
   - http://72.56.66.228/api/vacancies
   - http://72.56.66.228/api/experts
3. **Статус**: http://72.56.66.228/status

## ВОССТАНОВЛЕНИЕ ПРИ ПРОБЛЕМАХ

Если что-то пошло не так:
```bash
# Восстановить из бэкапа
cp -r /root/backup_20251005_121010/* /var/www/html/
systemctl restart nginx
```

## ЛОГИ ДЛЯ ОТЛАДКИ

```bash
# Логи приложения
tail -f /var/www/gsr_new/app.log

# Логи nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Системные логи
journalctl -u nginx -f
```

## КОНТАКТЫ

При проблемах проверьте:
- Статус сервера: systemctl status nginx
- Процессы: ps aux | grep python
- Порты: netstat -tlnp | grep :5000
