# УПРОЩЕННАЯ ВЕРСИЯ ПРИЛОЖЕНИЯ БЕЗ БАЗЫ ДАННЫХ
# Использует API ключи напрямую из config.py
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from config import Config
from api.heygen_client import HeyGenClient
from api.elevenlabs_client import ElevenLabsClient
import uuid
import os
from datetime import datetime
import json
import re
import io
import csv
from typing import List, Dict, Any, Optional
import requests

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SERVER_NAME'] = None  # Разрешить работу без SERVER_NAME
    
    # Отключить кеш Flask для production
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = None
    app.config['DEBUG'] = False  # Production mode
    
    # Принудительно отключить кеш шаблонов
    app.jinja_env.cache = None
    app.jinja_env.auto_reload = True
    
    # Initialize extensions (NO DATABASE)
    CORS(app)  # Добавляем CORS поддержку
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Функция для получения API ключей из config.py
    def _get_api_key(key_name: str) -> str:
        """Получить API ключ из config.py вместо базы данных"""
        return Config.DEFAULT_API_KEYS.get(key_name, '')
    
    def _get_additional_settings(module_name: str) -> dict:
        """Получить дополнительные настройки для модуля"""
        if module_name == 'vacancies':
            return {
                "default_sheet_url": "https://docs.google.com/spreadsheets/u/1/d/1I1AfpmNbd-K0Osd4Vh7npDCYSQr2a1t_KdT8ms9vgr4/edit?gid=718924971#gid=718924971"
            }
        return {}
    
    # Register blueprints
    from routes.vacancies import vacancies_bp
    from routes.trends import trends_bp
    app.register_blueprint(vacancies_bp)
    app.register_blueprint(trends_bp)
    
    # Основные маршруты
    @app.route('/')
    def index():
        return '''
        <h1>GSR Content Factory</h1>
        <p>Сервер работает!</p>
        <ul>
            <li><a href="/vacancies">Модуль вакансий</a></li>
            <li><a href="/trends">Модуль трендов</a></li>
        </ul>
        '''
    
    @app.route('/vacancies')
    def vacancies():
        return render_template('module_vacancies.html')
    
    @app.route('/trends')
    def trends():
        return '''
        <h1>Модуль трендов</h1>
        <p>Модуль трендов в разработке</p>
        '''
    
    # API маршруты для получения настроек (без базы данных)
    @app.route('/api/settings/<module_name>', methods=['GET'])
    def get_module_settings(module_name):
        """Получить настройки модуля из config.py"""
        try:
            api_keys = {
                'openai_api_key': _get_api_key('openai_api_key'),
                'elevenlabs_api_key': _get_api_key('elevenlabs_api_key'),
                'heygen_api_key': _get_api_key('heygen_api_key'),
                'apify_api_key': _get_api_key('apify_api_key'),
                'assemblyai_api_key': _get_api_key('assemblyai_api_key')
            }
            
            additional_settings = _get_additional_settings(module_name)
            
            return jsonify({
                'success': True,
                'api_keys': api_keys,
                'additional_settings': additional_settings
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/settings/<module_name>', methods=['POST'])
    def update_module_settings(module_name):
        """Обновить настройки модуля (только для совместимости, не сохраняет в БД)"""
        try:
            data = request.get_json()
            return jsonify({
                'success': True,
                'message': 'Настройки обновлены (в памяти)',
                'api_keys': data.get('api_keys', {}),
                'additional_settings': data.get('additional_settings', {})
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Обработка ошибок
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app, socketio

# Создаем экземпляр приложения для gunicorn
app, socketio = create_app()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
