# Deployment пакет для исправления Apify

## Создан: 2025-10-09 14:39:27

## Содержимое:
- `apify_client.py` - Исправленный файл с правильными параметрами
- `deploy.sh` - Скрипт автоматического развертывания
- `README.md` - Этот файл

## Исправления:
- Заменен `"profiles": [username]` на `"username": [username]` для актора xMc5Ga1oCONPmWJIa
- Заменен `"profiles": [username]` на `"username": [username]` для fallback актора apify/instagram-reel-scraper

## Как развернуть:
1. Убедитесь, что файл `server_key` существует
2. Запустите: `./deploy.sh`
3. Проверьте: http://72.56.66.228/module/trends

## Тестирование:
После развертывания протестируйте:
- Сбор рилсов для @alfa.resource.group.kg
- Отсутствие ошибки HTTP 400
- Корректное отображение результатов
