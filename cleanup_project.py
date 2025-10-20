#!/usr/bin/env python3
"""
Очистка проекта GSR - оставляем только нужные файлы
"""

import os
import glob

def cleanup_project():
    print("🧹 Очистка проекта GSR")
    print("=" * 40)
    
    # Файлы для удаления
    files_to_remove = [
        # Старые версии приложений
        "app_assemblyai_fixed.py",
        "app_current_backup_backup.py", 
        "app_current_backup_broken_*.py",
        "app_fastapi.py",
        "app_fixed_elevenlabs.py",
        "app_fixed_for_server.py",
        "app_for_server.py",
        "app_improved.py",
        "app_new.py",
        "app_restored_working.py",
        "app_server_original.py",
        "app_server_restored.py",
        "app_with_integration.py",
        "app_working_restore.py",
        
        # Тестовые файлы
        "test_*.py",
        "test_*.html",
        "test_*.json",
        
        # Скрипты восстановления
        "start_restored.py",
        "restore_*.py",
        "deploy_*.py",
        "check_*.py",
        "auto_*.py",
        
        # Улучшения (которые не нужны)
        "services/apify_service_improved.py",
        "services/elevenlabs_service_improved.py", 
        "routes/trends_improved.py",
        "templates/trends_improved.html",
        "app_improved.py",
        
        # Документация улучшений
        "TRENDS_IMPROVEMENTS.md",
        "FINAL_IMPROVEMENTS_REPORT.md",
        "SERVER_STATUS.md",
        "RESTORATION_COMPLETE.md",
        
        # Архивы
        "*.tar.gz",
        "backup_before_restore_*",
        "server_backup_*",
        "gsr_trends_module_backup_*",
        "module_trends_excel_version_*",
    ]
    
    removed_count = 0
    
    for pattern in files_to_remove:
        for file_path in glob.glob(pattern):
            if os.path.exists(file_path):
                try:
                    if os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                        print(f"🗂️  Удалена папка: {file_path}")
                    else:
                        os.remove(file_path)
                        print(f"🗑️  Удален файл: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Ошибка удаления {file_path}: {e}")
    
    print(f"\n✅ Удалено {removed_count} файлов/папок")
    print("🎯 Оставлены только нужные файлы:")
    print("   - app_local.py (локальная версия на порту 8000)")
    print("   - app_server.py (серверная версия)")
    print("   - app_live_backup_*.py (живучий бекап)")
    print("   - app_current_backup.py (основной файл)")

if __name__ == "__main__":
    cleanup_project()
