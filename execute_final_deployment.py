#!/usr/bin/env python3
"""
Выполнение финального развертывания на сервере
"""

import os
import shutil
import tarfile
from pathlib import Path
from datetime import datetime

def execute_final_deployment():
    """Выполнение финального развертывания"""
    print("🚀 ВЫПОЛНЕНИЕ ФИНАЛЬНОГО РАЗВЕРТЫВАНИЯ")
    print("=" * 60)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Создаем имя архива с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"gsr_final_deploy_{timestamp}.tar.gz"
    
    print(f"📁 Создаем архив: {archive_name}")
    
    # Список файлов для архива
    files_to_include = [
        'app_for_server_final.py',
        'config.py',
        'models.py',
        'requirements.txt',
        'run.py',
        'api/',
        'templates/',
        'static/',
        'modules/'
    ]
    
    # Создаем временную директорию
    temp_dir = Path(f"temp_final_deploy_{timestamp}")
    temp_dir.mkdir(exist_ok=True)
    
    print("📋 Копируем файлы:")
    copied_files = 0
    
    for item in files_to_include:
        source = Path(item)
        if source.exists():
            if source.is_file():
                shutil.copy2(source, temp_dir / source.name)
                print(f"   ✅ {item}")
                copied_files += 1
            else:
                shutil.copytree(source, temp_dir / source.name, dirs_exist_ok=True)
                print(f"   ✅ {item}/")
                copied_files += 1
        else:
            print(f"   ❌ {item} - НЕ НАЙДЕН")
    
    print(f"\n📊 Скопировано файлов/папок: {copied_files}")
    
    # Создаем инструкции для развертывания
    instructions = f"""# 🚀 ФИНАЛЬНЫЕ ИНСТРУКЦИИ ПО РАЗВЕРТЫВАНИЮ НА СЕРВЕРЕ

## 📦 Архив: {archive_name}
## ⏰ Создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
## ✅ Статус: Исправлен и готов к развертыванию

### 🔧 СПОСОБ 1: ЧЕРЕЗ ВЕБ-ПАНЕЛЬ ХОСТИНГА

1. **Войдите в панель управления хостингом**
   - Откройте файловый менеджер
   - Найдите папку с приложением (обычно `/var/www/gsr/` или `/public_html/`)

2. **Создайте резервную копию**
   - Скопируйте текущий `app.py` в `app_backup.py`
   - Сохраните текущую базу данных

3. **Загрузите новый архив**
   - Загрузите файл `{archive_name}`
   - Распакуйте его в папку с приложением

4. **Настройте приложение**
   - Переименуйте `app_for_server_final.py` в `app.py`
   - Установите права доступа: `chmod +x app.py`

5. **Установите зависимости**
   - Откройте терминал в панели управления
   - Выполните: `pip3 install -r requirements.txt`

6. **Запустите приложение**
   - Остановите текущее: `pkill -f 'python.*app.py'`
   - Запустите новое: `nohup python3 app.py > app.log 2>&1 &`

### 🔧 СПОСОБ 2: ЧЕРЕЗ SSH (если доступен)

```bash
# 1. Загрузите архив на сервер
scp {archive_name} user@72.56.66.228:/tmp/

# 2. Подключитесь к серверу
ssh user@72.56.66.228

# 3. Перейдите в папку с приложением
cd /var/www/gsr/

# 4. Создайте резервную копию
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz *.py *.html *.css *.js

# 5. Распакуйте новый архив
tar -xzf /tmp/{archive_name} --strip-components=1

# 6. Переименуйте основной файл
mv app_for_server_final.py app.py

# 7. Установите зависимости
pip3 install -r requirements.txt

# 8. Перезапустите приложение
pkill -f 'python.*app.py'
nohup python3 app.py > app.log 2>&1 &
```

### ✅ ПРОВЕРКА РАЗВЕРТЫВАНИЯ

1. **Откройте главную страницу**
   - http://72.56.66.228/
   - Должна загрузиться без ошибок

2. **Проверьте модули**
   - http://72.56.66.228/module/trends
   - http://72.56.66.228/module/vacancies
   - http://72.56.66.228/module/experts

3. **Проверьте отсутствие демо данных**
   - В модуле трендов нажмите "Собрать рилсы"
   - Убедитесь, что НЕТ текста "демо" или "пример контента"

### 🔧 УСТРАНЕНИЕ ПРОБЛЕМ

**Если приложение не запускается:**
```bash
# Проверьте логи
tail -f app.log

# Проверьте, что порт свободен
netstat -tlnp | grep :5000

# Проверьте права доступа
ls -la app.py
chmod +x app.py
```

**Если есть ошибки импорта:**
```bash
# Переустановите зависимости
pip3 install -r requirements.txt --force-reinstall

# Проверьте Python версию
python3 --version
```

**Если демо данные все еще есть:**
- Убедитесь, что заменили `app.py` на `app_for_server_final.py`
- Перезапустите приложение
- Очистите кэш браузера

### 📞 ПОДДЕРЖКА

Если возникли проблемы:
1. Проверьте логи: `tail -f app.log`
2. Убедитесь, что все файлы загружены
3. Проверьте права доступа к файлам
4. Убедитесь, что порт 5000 свободен

---
**Дата создания:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Архив:** {archive_name}
**Статус:** Исправлен и готов к развертыванию ✅
"""
    
    with open(temp_dir / "FINAL_DEPLOY_INSTRUCTIONS.md", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("   ✅ Созданы инструкции: FINAL_DEPLOY_INSTRUCTIONS.md")
    
    # Создаем архив
    print(f"\n📦 Создаем архив {archive_name}...")
    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(temp_dir, arcname="gsr_final_deploy")
    
    # Удаляем временную директорию
    shutil.rmtree(temp_dir)
    
    print(f"✅ Архив создан: {archive_name}")
    print(f"📏 Размер архива: {os.path.getsize(archive_name) / 1024 / 1024:.2f} MB")
    
    # Создаем скрипт загрузки
    script_name = f"upload_final_{archive_name.replace('.tar.gz', '')}.sh"
    
    script_content = f"""#!/bin/bash
# Скрипт для загрузки {archive_name} на сервер 72.56.66.228

echo "🚀 ФИНАЛЬНАЯ ЗАГРУЗКА НА СЕРВЕР 72.56.66.228"
echo "=========================================="

# Проверяем наличие архива
if [ ! -f "{archive_name}" ]; then
    echo "❌ Архив {archive_name} не найден!"
    exit 1
fi

echo "📦 Архив найден: {archive_name}"

# Создаем резервную копию на сервере
echo "💾 Создаем резервную копию на сервере..."
ssh root@72.56.66.228 "cd /var/www/gsr && tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz *.py *.html *.css *.js 2>/dev/null || true"

# Загружаем архив
echo "📤 Загружаем архив на сервер..."
scp {archive_name} root@72.56.66.228:/tmp/

# Распаковываем на сервере
echo "📁 Распаковываем на сервере..."
ssh root@72.56.66.228 "cd /var/www/gsr && tar -xzf /tmp/{archive_name} --strip-components=1"

# Переименовываем основной файл
echo "🔄 Переименовываем app_for_server_final.py в app.py..."
ssh root@72.56.66.228 "cd /var/www/gsr && mv app_for_server_final.py app.py"

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
ssh root@72.56.66.228 "cd /var/www/gsr && pip3 install -r requirements.txt"

# Перезапускаем приложение
echo "🔄 Перезапускаем приложение..."
ssh root@72.56.66.228 "cd /var/www/gsr && pkill -f 'python.*app.py' || true"
ssh root@72.56.66.228 "cd /var/www/gsr && nohup python3 app.py > app.log 2>&1 &"

# Ждем запуска
echo "⏳ Ждем запуска приложения..."
sleep 5

# Проверяем статус
echo "🔍 Проверяем статус..."
ssh root@72.56.66.228 "cd /var/www/gsr && ps aux | grep 'python.*app.py' | grep -v grep"

echo "✅ Финальное развертывание завершено!"
echo "🌐 Проверьте: http://72.56.66.228/"
"""
    
    with open(script_name, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Делаем скрипт исполняемым
    os.chmod(script_name, 0o755)
    
    print(f"✅ Скрипт создан: {script_name}")
    
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ СТАТУС")
    print("=" * 60)
    
    print("🎉 ФИНАЛЬНЫЙ ПАКЕТ ДЛЯ РАЗВЕРТЫВАНИЯ ГОТОВ!")
    print(f"📦 Архив: {archive_name}")
    print(f"📤 Скрипт загрузки: {script_name}")
    print(f"📋 Инструкции: FINAL_DEPLOY_INSTRUCTIONS.md")
    
    print("\n📞 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Проверьте сервер: python3 perform_server_check.py")
    print("2. Разверните пакет на сервере")
    print("3. Протестируйте работу")
    
    print(f"\n🔧 ДЛЯ АВТОМАТИЧЕСКОГО РАЗВЕРТЫВАНИЯ:")
    print(f"   ./{script_name}")
    
    print(f"\n🔧 ДЛЯ РУЧНОГО РАЗВЕРТЫВАНИЯ:")
    print(f"   Смотрите FINAL_DEPLOY_INSTRUCTIONS.md")
    
    return archive_name, script_name

if __name__ == "__main__":
    execute_final_deployment()
