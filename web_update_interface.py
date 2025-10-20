#!/usr/bin/env python3
"""
Веб-интерфейс для обновления сервера
"""

from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Обновление сервера GSR</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        .info { background-color: #d1ecf1; color: #0c5460; }
        button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .code { background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Обновление сервера GSR</h1>
        
        <div class="status info">
            <strong>Сервер:</strong> 72.56.66.228<br>
            <strong>Проблема:</strong> На сервере запущена старая версия кода с ошибкой "name 'HeyGenClient' is not defined"
        </div>
        
        <h2>📋 Инструкции по обновлению:</h2>
        
        <div class="code">
            <strong>1. Подключитесь к серверу по SSH:</strong><br>
            ssh root@72.56.66.228<br>
            Пароль: g2D,RytdQoSAYv
        </div>
        
        <div class="code">
            <strong>2. Остановите текущий сервер:</strong><br>
            pkill -f "python.*app"<br>
            pkill -f "flask"
        </div>
        
        <div class="code">
            <strong>3. Обновите код:</strong><br>
            # Замените файлы на исправленные версии<br>
            # app_current_backup.py - с импортом HeyGenClient<br>
            # models.py - без колонки redpolicy_pdf_path<br>
            # app.py - с allow_unsafe_werkzeug=True
        </div>
        
        <div class="code">
            <strong>4. Перезапустите сервер:</strong><br>
            python3 app.py
        </div>
        
        <h2>🔧 Автоматические действия:</h2>
        
        <button onclick="updateApiKey()">Обновить HeyGen API ключ</button>
        <button onclick="checkStatus()">Проверить статус сервера</button>
        <button onclick="testPipeline()">Тестировать пайплайн</button>
        
        <div id="results"></div>
    </div>
    
    <script>
        function updateApiKey() {
            fetch('/update_api_key', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('results').innerHTML = 
                        '<div class="status ' + (data.success ? 'success' : 'error') + '">' + data.message + '</div>';
                });
        }
        
        function checkStatus() {
            fetch('/check_status', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('results').innerHTML = 
                        '<div class="status ' + (data.success ? 'success' : 'error') + '">' + data.message + '</div>';
                });
        }
        
        function testPipeline() {
            fetch('/test_pipeline', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    document.getElementById('results').innerHTML = 
                        '<div class="status ' + (data.success ? 'success' : 'error') + '">' + data.message + '</div>';
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/update_api_key', methods=['POST'])
def update_api_key():
    try:
        response = requests.post("http://72.56.66.228/api/settings/vacancies", 
                               json={
                                   "api_keys": {
                                       "heygen_api_key": "ZjI2NmI4MGEzOTA0NDIwNzgxNjIzMjdjOWU0N2E3YWEtMTc2MDUxOTU5OQ=="
                                   }
                               })
        if response.status_code == 200:
            return jsonify({"success": True, "message": "✅ HeyGen API ключ обновлен на сервере"})
        else:
            return jsonify({"success": False, "message": f"❌ Ошибка обновления API ключа: {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Ошибка: {str(e)}"})

@app.route('/check_status', methods=['POST'])
def check_status():
    try:
        response = requests.post("http://72.56.66.228/api/vacancies/check-video-status", 
                               json={"video_id": "test"})
        if response.status_code == 200:
            data = response.json()
            if "HeyGenClient" in str(data):
                return jsonify({"success": False, "message": "❌ Сервер все еще использует старую версию кода. Нужно обновить код на сервере."})
            else:
                return jsonify({"success": True, "message": "✅ API работает корректно"})
        else:
            return jsonify({"success": False, "message": f"❌ Ошибка API: {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Ошибка: {str(e)}"})

@app.route('/test_pipeline', methods=['POST'])
def test_pipeline():
    try:
        response = requests.get("http://72.56.66.228/api/vacancies/test")
        if response.status_code == 200:
            return jsonify({"success": True, "message": "✅ Тестовые данные загружаются"})
        else:
            return jsonify({"success": False, "message": f"❌ Ошибка загрузки тестовых данных: {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Ошибка: {str(e)}"})

if __name__ == '__main__':
    print("🌐 Веб-интерфейс для обновления сервера запущен на http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=True)