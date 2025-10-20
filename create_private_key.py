#!/usr/bin/env python3
"""
Создание приватного SSH ключа для подключения к серверу
"""

import os
import subprocess

def create_private_key():
    """Создает приватный SSH ключ"""
    print("🔑 Создаю приватный SSH ключ...")
    
    try:
        # Генерируем новую пару ключей
        result = subprocess.run([
            "ssh-keygen", "-t", "rsa", "-b", "4096", "-f", "server_key", "-N", ""
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Приватный ключ создан: server_key")
            print("✅ Публичный ключ создан: server_key.pub")
            
            # Устанавливаем правильные права
            os.chmod("server_key", 0o600)
            os.chmod("server_key.pub", 0o644)
            
            print("✅ Права доступа установлены")
            
            # Показываем публичный ключ
            with open("server_key.pub", "r") as f:
                public_key = f.read().strip()
            
            print(f"\n📋 ПУБЛИЧНЫЙ КЛЮЧ ДЛЯ СЕРВЕРА:")
            print(f"{public_key}")
            print("\n🔧 ДОБАВЬТЕ ЭТОТ КЛЮЧ В ПАНЕЛЬ УПРАВЛЕНИЯ СЕРВЕРОМ!")
            
            return True
        else:
            print(f"❌ Ошибка создания ключа: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_connection():
    """Тестирует подключение"""
    print("\n🔍 Тестирую подключение...")
    
    try:
        result = subprocess.run([
            "ssh", "-i", "server_key", "-o", "StrictHostKeyChecking=no",
            "user@72.56.66.228", "echo 'SSH подключение работает'"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ SSH подключение работает!")
            print(f"📋 Ответ сервера: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ SSH ошибка: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def main():
    print("🚀 СОЗДАНИЕ SSH КЛЮЧА ДЛЯ СЕРВЕРА")
    print("="*50)
    
    # Создаем ключ
    if create_private_key():
        print("\n✅ КЛЮЧ СОЗДАН УСПЕШНО!")
        print("🔧 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Добавьте публичный ключ в панель управления сервером")
        print("2. Запустите: python3 ssh_key_update.py")
        
        # Тестируем подключение
        test_connection()
    else:
        print("❌ НЕ УДАЛОСЬ СОЗДАТЬ КЛЮЧ!")
        print("🔧 ВЫПОЛНИТЕ ВРУЧНУЮ:")
        print("1. ssh-keygen -t rsa -b 4096 -f server_key -N ''")
        print("2. chmod 600 server_key")
        print("3. Добавьте server_key.pub в панель управления")

if __name__ == "__main__":
    main()
