#!/usr/bin/env python3
"""
Быстрый тест Submagic API
Прямой Python скрипт для тестирования Submagic без Flask
"""

import requests
import json
import os
import glob
import time
from typing import Dict, Any

# Конфигурация
SUBMAGIC_API_KEY = "sk-f5cfec75ecd20466f31774ccd701dc42ff0aaa71602cd27cd1db2f6a43c5ab31"
SUBMAGIC_BASE_URL = "https://api.submagic.co"
SERVER_BASE_URL = "http://72.56.66.228"

def find_latest_video() -> str:
    """Находит последнее видео на сервере"""
    print("🔍 Ищем последнее видео на сервере...")
    
    # Ищем через API сервера
    try:
        response = requests.get(f"{SERVER_BASE_URL}/api/trends/test-video-url", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                video_url = data.get('video_url')
                print(f"✅ Найдено видео: {video_url}")
                return video_url
    except Exception as e:
        print(f"❌ Ошибка получения видео через API: {e}")
    
    # Fallback - используем последнее известное видео
    fallback_videos = [
        "http://72.56.66.228/static/video/caption_ab9279a3.mp4",
        "http://72.56.66.228/static/video/caption_a9487e76.mp4",
        "http://72.56.66.228/static/video/caption_ae7c953e.mp4"
    ]
    
    for video_url in fallback_videos:
        try:
            response = requests.head(video_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Fallback видео найдено: {video_url}")
                return video_url
        except:
            continue
    
    raise Exception("Не удалось найти доступное видео для тестирования")

def test_submagic_connection() -> bool:
    """Тестирует подключение к Submagic API"""
    print("🔗 Тестируем подключение к Submagic API...")
    
    try:
        headers = {
            "x-api-key": SUBMAGIC_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Попробуем health check
        response = requests.get(f"{SUBMAGIC_BASE_URL}/health", headers=headers, timeout=10)
        print(f"📡 Health check: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Submagic API доступен")
            return True
        else:
            print(f"⚠️ Submagic API вернул {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Submagic: {e}")
        return False

def test_submagic_templates() -> list:
    """Тестирует получение шаблонов Submagic"""
    print("📋 Тестируем получение шаблонов...")
    
    try:
        headers = {
            "x-api-key": SUBMAGIC_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{SUBMAGIC_BASE_URL}/v1/templates", headers=headers, timeout=10)
        print(f"📡 Templates API: {response.status_code}")
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Получено шаблонов: {len(templates)}")
            return templates
        else:
            print(f"⚠️ Templates API вернул {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Ошибка получения шаблонов: {e}")
        return []

def test_submagic_video_processing(video_url: str) -> Dict[str, Any]:
    """Тестирует обработку видео через Submagic"""
    print(f"🎬 Тестируем обработку видео: {video_url}")
    
    try:
        headers = {
            "x-api-key": SUBMAGIC_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Создаем проект с правильной структурой Submagic API
        payload = {
            "title": "Test Video Processing",
            "language": "ru",
            "videoUrl": video_url
        }
        
        print(f"📤 Отправляем запрос в Submagic: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{SUBMAGIC_BASE_URL}/v1/projects",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Создание проекта: {response.status_code}")
        print(f"📊 Ответ: {response.text}")
        
        if response.status_code == 201:
            project_data = response.json()
            project_id = project_data.get('id')
            print(f"✅ Проект создан: {project_id}")
            
            # Мониторим статус
            return monitor_project_status(project_id, headers)
        else:
            return {
                'success': False,
                'error': f"Ошибка создания проекта: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        print(f"❌ Ошибка обработки видео: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def monitor_project_status(project_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Мониторит статус проекта"""
    print(f"🔄 Мониторим статус проекта {project_id}...")
    
    max_attempts = 20  # 20 попыток по 10 секунд = 3.3 минуты
    for attempt in range(max_attempts):
        try:
            response = requests.get(
                f"{SUBMAGIC_BASE_URL}/v1/projects/{project_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                project_data = response.json()
                status = project_data.get('status', 'unknown')
                print(f"📊 Попытка {attempt + 1}: статус = {status}")
                
                if status == 'completed':
                    video_url = project_data.get('videoUrl')
                    print(f"✅ Проект завершен: {video_url}")
                    return {
                        'success': True,
                        'project_id': project_id,
                        'video_url': video_url,
                        'status': status
                    }
                elif status == 'failed':
                    error = project_data.get('error', 'Unknown error')
                    print(f"❌ Проект провалился: {error}")
                    return {
                        'success': False,
                        'error': f"Проект провалился: {error}"
                    }
                else:
                    print(f"⏳ Статус: {status}, ждем...")
                    time.sleep(10)
            else:
                print(f"⚠️ Ошибка проверки статуса: {response.status_code}")
                time.sleep(10)
                
        except Exception as e:
            print(f"❌ Ошибка мониторинга: {e}")
            time.sleep(10)
    
    return {
        'success': False,
        'error': f"Проект не завершился за {max_attempts * 10} секунд"
    }

def main():
    """Основная функция тестирования"""
    print("🧪 БЫСТРЫЙ ТЕСТ SUBMAGIC API")
    print("=" * 50)
    
    # 1. Находим видео
    try:
        video_url = find_latest_video()
    except Exception as e:
        print(f"❌ Не удалось найти видео: {e}")
        return
    
    # 2. Тестируем подключение
    if not test_submagic_connection():
        print("❌ Submagic API недоступен, но продолжаем тест...")
    
    # 3. Тестируем шаблоны
    templates = test_submagic_templates()
    if templates:
        template_names = [t.get('name', 'Unknown') for t in templates[:3]] if isinstance(templates, list) else ['Unknown']
        print(f"📋 Доступные шаблоны: {template_names}")
    
    # 4. Тестируем обработку видео
    print(f"\n🎬 ТЕСТИРУЕМ ОБРАБОТКУ ВИДЕО")
    print("-" * 30)
    result = test_submagic_video_processing(video_url)
    
    # 5. Результаты
    print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 30)
    
    if result.get('success'):
        print(f"✅ УСПЕХ!")
        print(f"🎬 Проект: {result.get('project_id')}")
        print(f"🔗 Видео: {result.get('video_url')}")
        print(f"📊 Статус: {result.get('status')}")
    else:
        print(f"❌ ОШИБКА: {result.get('error')}")
    
    print(f"\n🏁 Тест завершен")

if __name__ == "__main__":
    main()
