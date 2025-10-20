#!/usr/bin/env python3
"""
Простой HTTP сервер для тестирования настроек голоса
"""
import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, parse_qs
import json

# Добавляем путь к проекту
sys.path.append('.')

class AudioHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/test_audio_settings.html'
        return super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/trends/generate-audio':
            self.handle_audio_generation()
        else:
            self.send_error(404)
    
    def handle_audio_generation(self):
        """Обработка запроса генерации аудио"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"🎵 Запрос генерации аудио:")
            print(f"   Текст: {data.get('text', '')[:50]}...")
            print(f"   Голос: {data.get('voice_id', '')}")
            print(f"   Модель: {data.get('model_id', '')}")
            print(f"   Speed: {data.get('speed', 1.0)}")
            print(f"   Stability: {data.get('stability', 0.5)}")
            print(f"   Similarity: {data.get('similarity_boost', 0.5)}")
            
            # Имитируем генерацию аудио
            import uuid
            audio_filename = f"test_audio_{uuid.uuid4().hex}.mp3"
            audio_url = f"/static/audio/{audio_filename}"
            
            # Создаем директорию если не существует
            os.makedirs("static/audio", exist_ok=True)
            
            # Создаем тестовый MP3 файл
            test_audio_path = f"static/audio/{audio_filename}"
            with open(test_audio_path, 'wb') as f:
                # Простой MP3 заголовок
                mp3_header = bytes([
                    0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
                ])
                # Создаем ~3 секунды тишины
                audio_data = mp3_header * 300
                f.write(audio_data)
            
            # Отправляем ответ
            response = {
                'success': True,
                'audio_url': audio_url,
                'message': 'Аудио сгенерировано с новыми настройками!'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Ошибка обработки запроса: {e}")
            error_response = {
                'success': False,
                'message': f'Ошибка: {str(e)}'
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

if __name__ == "__main__":
    PORT = 8080
    
    print(f"🚀 Запускаем HTTP сервер на порту {PORT}")
    print(f"🌐 Откройте: http://localhost:{PORT}")
    print("🎵 Тестируем новые настройки голоса ElevenLabs")
    
    with socketserver.TCPServer(("", PORT), AudioHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Сервер остановлен")
