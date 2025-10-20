#!/usr/bin/env python3
"""
ПОЛНОЕ ОБНОВЛЕНИЕ СЕРВЕРА - УДАЛЯЕМ ВСЕ И ЗАЛИВАЕМ ЛОКАЛЬНУЮ ВЕРСИЮ
"""

import os
import shutil
import subprocess
import time
from datetime import datetime

def create_backup():
    """Создает резервную копию текущего состояния"""
    print("📦 СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ")
    print("="*50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"server_backup_{timestamp}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Копируем основные файлы
        important_files = [
            'app.py',
            'models.py', 
            'config.py',
            'requirements.txt',
            'templates/',
            'static/',
            'api/',
            'modules/',
            'instance/'
        ]
        
        for item in important_files:
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.copytree(item, f"{backup_dir}/{item}")
                    print(f"✅ Скопирована папка: {item}")
                else:
                    shutil.copy2(item, f"{backup_dir}/{item}")
                    print(f"✅ Скопирован файл: {item}")
            else:
                print(f"⚠️ Не найден: {item}")
        
        print(f"\n✅ Резервная копия создана: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return None

def prepare_local_version():
    """Подготавливает локальную версию для загрузки"""
    print("\n🔧 ПОДГОТОВКА ЛОКАЛЬНОЙ ВЕРСИИ")
    print("="*50)
    
    # Создаем папку для загрузки
    upload_dir = "server_upload_package"
    
    try:
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Копируем основные файлы
        files_to_copy = [
            'app.py',
            'models.py',
            'config.py', 
            'requirements.txt',
            'run.py',
            'start.sh'
        ]
        
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, f"{upload_dir}/{file}")
                print(f"✅ Подготовлен: {file}")
        
        # Копируем папки
        folders_to_copy = [
            'templates',
            'static', 
            'api',
            'modules',
            'instance'
        ]
        
        for folder in folders_to_copy:
            if os.path.exists(folder):
                shutil.copytree(folder, f"{upload_dir}/{folder}")
                print(f"✅ Подготовлена папка: {folder}")
        
        # Создаем архив
        archive_name = f"gsr_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        subprocess.run([
            'tar', '-czf', archive_name, '-C', upload_dir, '.'
        ], check=True)
        
        print(f"\n✅ Создан архив для загрузки: {archive_name}")
        return archive_name, upload_dir
        
    except Exception as e:
        print(f"❌ Ошибка подготовки: {e}")
        return None, None

def create_upload_script(archive_name):
    """Создает скрипт для загрузки на сервер"""
    script_content = f"""#!/bin/bash
# Скрипт полного обновления сервера 72.56.66.228

echo "🚀 ПОЛНОЕ ОБНОВЛЕНИЕ СЕРВЕРА"
echo "=============================="

# Проверяем архив
if [ ! -f "{archive_name}" ]; then
    echo "❌ Архив {archive_name} не найден"
    exit 1
fi

echo "✅ Архив найден: {archive_name}"

# Создаем резервную копию на сервере
echo "📦 Создание резервной копии на сервере..."
ssh root@72.56.66.228 "mkdir -p /root/server_backup_$(date +%Y%m%d_%H%M%S) && cp -r /var/www/gsr/* /root/server_backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true"

# Останавливаем приложение
echo "⏹️ Остановка приложения..."
ssh root@72.56.66.228 "pkill -f 'python.*app.py' || true"

# Загружаем архив
echo "📤 Загрузка архива на сервер..."
scp {archive_name} root@72.56.66.228:/tmp/

# Распаковываем на сервере
echo "📦 Распаковка архива на сервере..."
ssh root@72.56.66.228 "
    cd /var/www/gsr || mkdir -p /var/www/gsr && cd /var/www/gsr
    rm -rf * .*
    tar -xzf /tmp/{archive_name}
    chmod +x *.py *.sh 2>/dev/null || true
    rm /tmp/{archive_name}
"

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
ssh root@72.56.66.228 "
    cd /var/www/gsr
    pip3 install -r requirements.txt --upgrade
"

# Запускаем приложение
echo "🚀 Запуск приложения..."
ssh root@72.56.66.228 "
    cd /var/www/gsr
    nohup python3 app.py > app.log 2>&1 &
    sleep 3
    ps aux | grep python
"

# Проверяем статус
echo "🔍 Проверка статуса..."
sleep 5
curl -s http://72.56.66.228/ > /dev/null && echo "✅ Сервер работает!" || echo "❌ Сервер не отвечает"

echo "🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО!"
echo "🌐 Откройте: http://72.56.66.228"
"""
    
    with open("upload_to_server.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("upload_to_server.sh", 0o755)
    print("✅ Создан скрипт upload_to_server.sh")

def create_manual_instructions(archive_name):
    """Создает инструкции для ручной загрузки"""
    instructions = f"""# 🚀 ПОЛНОЕ ОБНОВЛЕНИЕ СЕРВЕРА - РУЧНАЯ ЗАГРУЗКА

## 📦 Готовые файлы:
- **{archive_name}** - Полный архив проекта
- **upload_to_server.sh** - Автоматический скрипт загрузки

## 🔧 СПОСОБ 1: Автоматический скрипт
```bash
./upload_to_server.sh
```

## 🔧 СПОСОБ 2: Ручная загрузка

### Шаг 1: Подключение к серверу
```bash
ssh root@72.56.66.228
```

### Шаг 2: Резервная копия
```bash
mkdir -p /root/server_backup_$(date +%Y%m%d_%H%M%S)
cp -r /var/www/gsr/* /root/server_backup_$(date +%Y%m%d_%H%M%S)/
```

### Шаг 3: Остановка приложения
```bash
pkill -f 'python.*app.py'
```

### Шаг 4: Загрузка архива
```bash
# На локальной машине:
scp {archive_name} root@72.56.66.228:/tmp/
```

### Шаг 5: Распаковка
```bash
# На сервере:
cd /var/www/gsr
rm -rf * .*
tar -xzf /tmp/{archive_name}
chmod +x *.py *.sh
rm /tmp/{archive_name}
```

### Шаг 6: Установка зависимостей
```bash
pip3 install -r requirements.txt --upgrade
```

### Шаг 7: Запуск
```bash
nohup python3 app.py > app.log 2>&1 &
```

### Шаг 8: Проверка
```bash
curl http://72.56.66.228/
```

## 🎯 Ожидаемый результат:
- ✅ Все API endpoints работают
- ✅ Демо данные убраны
- ✅ Реальные данные от Apify
- ✅ Все модули функционируют

## 🔍 Проверка после обновления:
1. Откройте http://72.56.66.228/module/trends
2. Нажмите "Собрать рилсы конкурентов"
3. Убедитесь, что нет демо данных
4. Проверьте все модули

## 📞 Если что-то пошло не так:
1. Восстановите из резервной копии: `cp -r /root/server_backup_*/ /var/www/gsr/`
2. Перезапустите: `python3 app.py`
3. Проверьте логи: `tail -f app.log`
"""
    
    with open("MANUAL_SERVER_UPDATE.md", "w") as f:
        f.write(instructions)
    
    print("✅ Созданы инструкции MANUAL_SERVER_UPDATE.md")

def main():
    print("🚀 ПОЛНОЕ ОБНОВЛЕНИЕ СЕРВЕРА")
    print("Удаляем все на сервере и заливаем локальную версию")
    print("="*60)
    
    # Создаем резервную копию
    backup_dir = create_backup()
    if not backup_dir:
        print("❌ Не удалось создать резервную копию")
        return
    
    # Подготавливаем локальную версию
    archive_name, upload_dir = prepare_local_version()
    if not archive_name:
        print("❌ Не удалось подготовить локальную версию")
        return
    
    # Создаем скрипт загрузки
    create_upload_script(archive_name)
    
    # Создаем инструкции
    create_manual_instructions(archive_name)
    
    print("\n" + "="*60)
    print("📋 ГОТОВО К ЗАГРУЗКЕ!")
    print("="*60)
    print(f"📦 Архив: {archive_name}")
    print(f"📁 Папка: {upload_dir}")
    print(f"📦 Резервная копия: {backup_dir}")
    print(f"🚀 Скрипт: upload_to_server.sh")
    print(f"📖 Инструкции: MANUAL_SERVER_UPDATE.md")
    print()
    print("🎯 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Запустите: ./upload_to_server.sh")
    print("2. Или следуйте инструкциям в MANUAL_SERVER_UPDATE.md")
    print("3. Проверьте результат: http://72.56.66.228")

if __name__ == "__main__":
    main()
