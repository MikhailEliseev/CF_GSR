#!/usr/bin/env python3
"""
Веб-интерфейс для исправления AssemblyAI
"""

from flask import Flask, request, jsonify, render_template_string, send_file
import os
import subprocess
import time
import requests

app = Flask(__name__)

# HTML шаблон
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Исправление AssemblyAI</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px 5px; }
        button:hover { background: #0056b3; }
        .danger { background: #dc3545; }
        .danger:hover { background: #c82333; }
        .success-btn { background: #28a745; }
        .success-btn:hover { background: #218838; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .file-info { background: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .code-block { background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 ИСПРАВЛЕНИЕ ASSEMBLYAI</h1>
        
        <div class="file-info">
            <h3>📁 Готовые файлы для исправления:</h3>
            <ul>
                <li><strong>app_assemblyai_fixed.py</strong> - Версия с исправленным AssemblyAI</li>
                <li><strong>api/assemblyai_client.py</strong> - Исправленный клиент AssemblyAI</li>
                <li><strong>test_assemblyai.py</strong> - Тест AssemblyAI</li>
            </ul>
        </div>
        
        <div id="status"></div>
        
        <div style="text-align: center; margin: 30px 0;">
            <button onclick="checkServer()">🔍 Проверить сервер</button>
            <button onclick="downloadFiles()" class="success-btn">📥 Скачать файлы</button>
            <button onclick="showInstructions()">📋 Показать инструкции</button>
            <button onclick="testAssemblyAI()" class="danger">🧪 Тест AssemblyAI</button>
        </div>
        
        <div id="content"></div>
    </div>

    <script>
        function checkServer() {
            document.getElementById('status').innerHTML = '<div class="info">🔍 Проверяем сервер...</div>';
            
            fetch('/api/check-server')
                .then(response => response.json())
                .then(data => {
                    let statusClass = 'info';
                    if (data.status === 200) statusClass = 'success';
                    else if (data.status === 502) statusClass = 'error';
                    
                    document.getElementById('status').innerHTML = 
                        `<div class="${statusClass}">📊 Статус сервера: ${data.status}<br>${data.message}</div>`;
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = 
                        `<div class="error">❌ Ошибка проверки: ${error}</div>`;
                });
        }
        
        function downloadFiles() {
            document.getElementById('content').innerHTML = 
                '<div class="info">📥 Подготавливаем файлы для скачивания...</div>';
            
            fetch('/api/prepare-files')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('content').innerHTML = 
                            '<div class="success">✅ Файлы готовы! Скачайте их и загрузите на сервер.</div>' +
                            '<div style="margin: 20px 0;">' +
                            '<a href="/download/app_assemblyai_fixed.py" download style="display: inline-block; margin: 10px; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">📥 Скачать app_assemblyai_fixed.py</a>' +
                            '<a href="/download/assemblyai_fix.sh" download style="display: inline-block; margin: 10px; padding: 10px 20px; background: #17a2b8; color: white; text-decoration: none; border-radius: 5px;">📥 Скачать assemblyai_fix.sh</a>' +
                            '<a href="/download/test_assemblyai.py" download style="display: inline-block; margin: 10px; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px;">📥 Скачать тест</a>' +
                            '</div>';
                    } else {
                        document.getElementById('content').innerHTML = 
                            `<div class="error">❌ Ошибка: ${data.error}</div>`;
                    }
                });
        }
        
        function showInstructions() {
            document.getElementById('content').innerHTML = 
                '<div class="info">' +
                '<h3>📋 Инструкции по исправлению AssemblyAI:</h3>' +
                '<ol>' +
                '<li><strong>Скачайте файлы:</strong> Нажмите "Скачать файлы" выше</li>' +
                '<li><strong>Подключитесь к серверу:</strong> Через веб-панель хостинга или SSH</li>' +
                '<li><strong>Найдите папку с приложением:</strong><br><code>find / -name "app.py" 2>/dev/null</code></li>' +
                '<li><strong>Перейдите в папку:</strong><br><code>cd /path/to/your/app</code></li>' +
                '<li><strong>Создайте резервную копию:</strong><br><code>cp app.py app_backup.py</code></li>' +
                '<li><strong>Загрузите исправленный файл:</strong> Замените app.py на app_assemblyai_fixed.py</li>' +
                '<li><strong>Остановите приложение:</strong><br><code>pkill -f python</code></li>' +
                '<li><strong>Запустите приложение:</strong><br><code>python3 app.py</code></li>' +
                '</ol>' +
                '<div class="warning">⚠️ После исправления проверьте: http://72.56.66.228/module/trends</div>' +
                '</div>';
        }
        
        function testAssemblyAI() {
            document.getElementById('content').innerHTML = 
                '<div class="info">' +
                '<h3>🧪 Тестирование AssemblyAI:</h3>' +
                '<div class="code-block">' +
                '# Запустите тест локально:<br>' +
                'python3 test_assemblyai.py<br><br>' +
                '# Или на сервере:<br>' +
                'python3 test_assemblyai.py<br><br>' +
                '# Проверьте API ключ:<br>' +
                'echo $ASSEMBLYAI_API_KEY<br><br>' +
                '# Установите API ключ:<br>' +
                'export ASSEMBLYAI_API_KEY="ваш_ключ"<br>' +
                '</div>' +
                '<div class="warning">⚠️ AssemblyAI будет работать в демо-режиме без API ключа</div>' +
                '</div>';
        }
        
        // Автоматическая проверка при загрузке
        window.onload = function() {
            checkServer();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/check-server')
def check_server():
    """Проверяет статус сервера"""
    try:
        response = requests.get("http://72.56.66.228", timeout=10)
        status = response.status_code
        
        if status == 200:
            message = "✅ Сервер работает!"
        elif status == 502:
            message = "❌ Приложение не запущено (502 Bad Gateway)"
        else:
            message = f"⚠️ Неожиданный статус: {status}"
            
        return jsonify({
            'status': status,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"❌ Ошибка подключения: {e}"
        })

@app.route('/api/prepare-files')
def prepare_files():
    """Подготавливает файлы для скачивания"""
    try:
        # Проверяем наличие файлов
        files_to_check = [
            'app_assemblyai_fixed.py',
            'assemblyai_fix.sh',
            'test_assemblyai.py'
        ]
        
        missing_files = []
        for file in files_to_check:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            return jsonify({
                'success': False,
                'error': f"Отсутствуют файлы: {', '.join(missing_files)}"
            })
        
        return jsonify({
            'success': True,
            'message': 'Файлы готовы для скачивания'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание файлов"""
    allowed_files = [
        'app_assemblyai_fixed.py',
        'assemblyai_fix.sh',
        'test_assemblyai.py'
    ]
    
    if filename not in allowed_files:
        return "Файл не найден", 404
    
    if not os.path.exists(filename):
        return "Файл не найден", 404
    
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    print("🚀 ВЕБ-ИНТЕРФЕЙС ДЛЯ ИСПРАВЛЕНИЯ ASSEMBLYAI")
    print("="*60)
    print("🌐 Откройте в браузере: http://localhost:5001")
    print("📁 Скачайте файлы и исправьте AssemblyAI")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
