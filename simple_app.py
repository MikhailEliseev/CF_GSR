#!/usr/bin/env python3
"""
Простое Flask приложение для тестирования
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Простые данные для тестирования
competitors = [
    {"id": 1, "name": "test_competitor", "platform": "tiktok", "username": "test_user"}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/module/trends')
def module_trends():
    return render_template('module_trends.html')

@app.route('/api/competitors', methods=['GET'])
def get_competitors():
    return jsonify(competitors)

@app.route('/api/competitors', methods=['POST'])
def add_competitor():
    data = request.get_json()
    new_competitor = {
        "id": len(competitors) + 1,
        "name": data.get('name', ''),
        "platform": data.get('platform', 'tiktok'),
        "username": data.get('username', '')
    }
    competitors.append(new_competitor)
    return jsonify({"success": True, "message": "Конкурент добавлен"})

@app.route('/api/trends/collect-reels', methods=['POST'])
def collect_reels():
    data = request.get_json()
            return jsonify({
        "success": True,
        "message": "Рилсы собраны",
        "reels": [
            {"id": 1, "title": "Тестовый рилс", "url": "https://example.com/reel1"},
            {"id": 2, "title": "Еще один рилс", "url": "https://example.com/reel2"}
        ]
    })

@app.route('/api/trends/voices', methods=['GET'])
def get_voices():
    return jsonify([
        {"id": "voice1", "name": "Тестовый голос 1"},
        {"id": "voice2", "name": "Тестовый голос 2"}
    ])

if __name__ == '__main__':
    print("🚀 Запускаем простое приложение...")
    app.run(host='0.0.0.0', port=5001, debug=False)