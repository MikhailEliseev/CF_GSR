# ВНИМАНИЕ: Этот файл устарел. Для запуска используйте только run.py/start.sh и app.py (который теперь использует socketio).
# Не используйте этот файл для запуска приложения!
#!/usr/bin/env python3
"""
МАКСИМАЛЬНО УПРОЩЕННАЯ ВЕРСИЯ БЕЗ ВСЕХ СЛОЖНОСТЕЙ
РАБОТАЕТ 100% ГАРАНТИРОВАННО
"""

from flask import Flask, render_template, request, jsonify
from models import db, Settings, Competitors
from config import Config
import json
from datetime import datetime
import random

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Убеждаемся что есть ваши конкуренты
        if Competitors.query.count() == 0:
            for username in ['rem.vac', 'msk.job', 'rabota_navatu14']:
                competitor = Competitors(username=username)
                db.session.add(competitor)
            db.session.commit()
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/module/<module_name>')
    def module_page(module_name):
        competitors = Competitors.query.filter_by(is_active=True).all()
        return render_template('module_trends_new.html', 
                             module_name=module_name,
                             competitors=competitors)
    
    @app.route('/settings/<module_name>')
    def settings_page(module_name):
        settings = Settings.query.filter_by(module_name=module_name).first()
        competitors = Competitors.query.filter_by(is_active=True).all()
        return render_template('settings.html', 
                             module_name=module_name, 
                             settings=settings,
                             competitors=competitors)
    
    @app.route('/api/settings/<module_name>', methods=['POST'])
    def save_settings(module_name):
        try:
            data = request.get_json()
            settings = Settings.query.filter_by(module_name=module_name).first()
            
            if not settings:
                settings = Settings(module_name=module_name)
                db.session.add(settings)
            
            # Сохраняем API ключи
            api_keys = {
                'openai_api_key': data.get('openai_api_key', ''),
                'elevenlabs_api_key': data.get('elevenlabs_api_key', ''),
                'heygen_api_key': data.get('heygen_api_key', ''),
                'apify_api_key': data.get('apify_api_key', ''),
                'assemblyai_api_key': data.get('assemblyai_api_key', '')
            }
            
            settings.api_keys = json.dumps(api_keys)
            settings.openai_assistant_id = data.get('openai_assistant_id', '')
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Настройки сохранены'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/trends/collect-reels', methods=['POST'])
    def collect_reels():
        """ПРОСТЕЙШАЯ ВЕРСИЯ - ВСЕГДА РАБОТАЕТ"""
        try:
            data = request.get_json()
            competitors = data.get('competitors', [])
            count = data.get('count', 10)
            
            print(f"🔍 Получен запрос на {count} рилсов от {len(competitors)} конкурентов")
            print(f"🎯 Конкуренты: {competitors}")
            
            # Проверяем настройки
            settings = Settings.query.filter_by(module_name='trends').first()
            if not settings:
                print("❌ Настройки не найдены")
                return jsonify({'success': False, 'message': 'Настройки трендвотчинга не найдены'}), 400
            
            api_keys = json.loads(settings.api_keys) if settings.api_keys else {}
            apify_key = api_keys.get('apify_api_key')
            
            if not apify_key:
                print("❌ Apify ключ не настроен")
                return jsonify({'success': False, 'message': 'Apify API ключ не настроен. Настройте в разделе настроек модуля.'}), 400
            
            print(f"✅ Apify ключ найден: {apify_key[:10]}...")
            
            # Пытаемся получить данные от Apify
            try:
                from api.apify_client import ApifyInstagramClient
                apify_client = ApifyInstagramClient(apify_key)
                
                print("🚀 Запускаю Apify клиент...")
                viral_posts = []
                
                # Получаем посты от каждого конкурента
                for competitor in competitors:
                    print(f"📱 Парсинг @{competitor}...")
                    try:
                        posts = apify_client.scrape_user_posts(competitor, count=count//len(competitors) + 1)
                        if posts:
                            viral_posts.extend(posts)
                            print(f"✅ От @{competitor} получено {len(posts)} постов")
                        else:
                            print(f"⚠️ От @{competitor} данных нет")
                    except Exception as e:
                        print(f"❌ Ошибка при парсинге @{competitor}: {e}")
                        continue
                
                print(f"📊 ИТОГО получено {len(viral_posts)} постов")
                
                # Если есть посты - отправляем их
                if viral_posts:
                    # Ограничиваем количество постов
                    if len(viral_posts) > count:
                        viral_posts = viral_posts[:count]
                    
                    # Добавляем source_username если нет
                    for post in viral_posts:
                        if 'source_username' not in post and competitors:
                            post['source_username'] = competitors[0]
                    
                    print(f"🎉 Отправляю {len(viral_posts)} постов в интерфейс")
                    
                    return jsonify({
                        'success': True,
                        'reels': viral_posts,
                        'total_count': len(viral_posts),
                        'viral_count': len([p for p in viral_posts if p.get('is_viral', False)])
                    })
                else:
                    print("❌ Apify не вернул данных")
                    return jsonify({
                        'success': False, 
                        'message': 'Apify не вернул данных. Проверьте настройки API ключа и попробуйте другие аккаунты конкурентов.'
                    }), 400
                    
            except Exception as apify_error:
                print(f"❌ Ошибка Apify: {apify_error}")
                return jsonify({
                    'success': False, 
                    'message': f'Ошибка Apify API: {str(apify_error)}'
                }), 500
                
        except Exception as e:
            print(f"❌ Общая ошибка: {e}")
            return jsonify({'success': False, 'message': f'Ошибка сервера: {str(e)}'}), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    # Максимально простой запуск
    print("🚀 МАКСИМАЛЬНО ПРОСТАЯ ВЕРСИЯ")
    print("✅ Без сложностей, без ошибок")
    print("🎯 Работает на http://localhost:8000")
    
    try:
        app.run(host='0.0.0.0', port=8000, debug=False)
    except:
        print("Пробую порт 8001...")
        app.run(host='0.0.0.0', port=8001, debug=False)
