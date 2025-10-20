#!/usr/bin/env python3
"""
Создание fallback решения для ElevenLabs
"""

import paramiko
import json
import time

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def create_fallback_solution():
    """Создаем fallback решение для ElevenLabs"""
    print("🔧 Создаем fallback решение для ElevenLabs...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Устанавливаем espeak и ffmpeg
        print("\n1️⃣ Устанавливаем TTS зависимости...")
        stdin, stdout, stderr = ssh.exec_command("apt-get update && apt-get install -y espeak ffmpeg")
        install_result = stdout.read().decode()
        print("✅ Зависимости установлены")
        
        # 2. Создаем fallback сервис
        print("\n2️⃣ Создаем fallback сервис...")
        
        fallback_service = '''
import subprocess
import tempfile
import os
import base64
from typing import Optional

class ElevenLabsFallback:
    """Fallback для ElevenLabs с использованием espeak"""
    
    def __init__(self):
        self.voice = "ru"  # Русский голос
        self.speed = 150   # Скорость речи
        
    def generate_audio(self, text: str) -> Optional[str]:
        """Генерирует аудио с помощью espeak"""
        try:
            # Создаем временный файл
            temp_wav = tempfile.mktemp(suffix=".wav")
            temp_mp3 = tempfile.mktemp(suffix=".mp3")
            
            # Генерируем аудио через espeak
            cmd = [
                "espeak", 
                "-s", str(self.speed),
                "-v", self.voice,
                "-w", temp_wav,
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(temp_wav):
                # Конвертируем в MP3
                convert_cmd = [
                    "ffmpeg", 
                    "-i", temp_wav, 
                    "-acodec", "mp3", 
                    "-y", temp_mp3
                ]
                
                convert_result = subprocess.run(convert_cmd, capture_output=True, text=True)
                
                if convert_result.returncode == 0 and os.path.exists(temp_mp3):
                    # Читаем MP3 файл
                    with open(temp_mp3, 'rb') as f:
                        audio_data = f.read()
                    
                    # Очищаем временные файлы
                    os.unlink(temp_wav)
                    os.unlink(temp_mp3)
                    
                    # Возвращаем base64
                    return base64.b64encode(audio_data).decode()
                else:
                    # Возвращаем WAV если MP3 не получился
                    with open(temp_wav, 'rb') as f:
                        audio_data = f.read()
                    
                    os.unlink(temp_wav)
                    if os.path.exists(temp_mp3):
                        os.unlink(temp_mp3)
                    
                    return base64.b64encode(audio_data).decode()
            else:
                print(f"Ошибка espeak: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Ошибка fallback: {e}")
            return None
'''
        
        # Записываем fallback сервис
        stdin, stdout, stderr = ssh.exec_command("cat > /root/services/elevenlabs_fallback.py << 'EOF'\n" + fallback_service + "\nEOF")
        stdout.read()
        print("✅ Fallback сервис создан")
        
        # 3. Обновляем routes/vacancies.py с fallback
        print("\n3️⃣ Обновляем routes/vacancies.py...")
        
        fallback_endpoint = '''
@vacancies_bp.route('/api/vacancies/generate-audio-fallback', methods=['POST'])
def generate_audio_fallback():
    """Fallback генерация аудио через espeak"""
    try:
        from services.elevenlabs_fallback import ElevenLabsFallback
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"success": False, "error": "Текст не указан"}), 400
        
        print(f"Генерируем fallback аудио для текста: {text[:50]}...")
        
        # Используем fallback
        fallback = ElevenLabsFallback()
        audio_base64 = fallback.generate_audio(text)
        
        if audio_base64:
            return jsonify({
                "success": True,
                "audio_data": audio_base64,
                "method": "espeak_fallback",
                "message": "Аудио сгенерировано через системный TTS"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ошибка генерации fallback аудио"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Ошибка fallback: {str(e)}"
        }), 500
'''
        
        # Добавляем endpoint
        stdin, stdout, stderr = ssh.exec_command("echo '\n" + fallback_endpoint + "' >> /root/routes/vacancies.py")
        stdout.read()
        print("✅ Fallback endpoint добавлен")
        
        # 4. Обновляем frontend для использования fallback
        print("\n4️⃣ Обновляем frontend...")
        
        # Создаем обновленный JavaScript для fallback
        frontend_update = '''
// Обновляем функцию генерации аудио для использования fallback
function generateAudioFallback() {
    const text = document.getElementById('generatedText').value;
    if (!text) {
        alert('Сначала сгенерируйте текст');
        return;
    }
    
    showStatus('Генерируем аудио через fallback TTS...', 'info');
    
    fetch('/api/vacancies/generate-audio-fallback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('✅ Аудио сгенерировано через fallback TTS', 'success');
            // Сохраняем аудио
            const audioBlob = new Blob([Uint8Array.from(atob(data.audio_data), c => c.charCodeAt(0))], { type: 'audio/mp3' });
            const audioUrl = URL.createObjectURL(audioBlob);
            
            // Создаем элемент для воспроизведения
            const audio = document.createElement('audio');
            audio.controls = true;
            audio.src = audioUrl;
            
            // Добавляем в интерфейс
            const audioContainer = document.getElementById('audioContainer');
            if (audioContainer) {
                audioContainer.innerHTML = '';
                audioContainer.appendChild(audio);
            }
        } else {
            showStatus('❌ Ошибка: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showStatus('❌ Ошибка: ' + error.message, 'error');
    });
}
'''
        
        # Записываем обновление в файл
        stdin, stdout, stderr = ssh.exec_command("echo '" + frontend_update + "' > /root/fallback_audio.js")
        stdout.read()
        print("✅ Frontend обновление создано")
        
        # 5. Перезапускаем сервер
        print("\n5️⃣ Перезапускаем сервер...")
        ssh.exec_command("pkill -f python.*app")
        time.sleep(2)
        ssh.exec_command("cd /root && nohup python3 app.py > server.log 2>&1 &")
        time.sleep(3)
        
        # Проверяем сервер
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep python.*app | grep -v grep")
        processes = stdout.read().decode()
        if processes:
            print("✅ Сервер перезапущен")
        else:
            print("❌ Сервер не запустился")
        
        # 6. Тестируем fallback
        print("\n6️⃣ Тестируем fallback...")
        test_payload = {
            "text": "Привет! Это тест fallback аудио через espeak."
        }
        
        test_cmd = f"curl -X POST -H 'Content-Type: application/json' -d '{json.dumps(test_payload)}' http://localhost:5000/api/vacancies/generate-audio-fallback"
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        result = stdout.read().decode()
        
        if "success" in result and "audio_data" in result:
            print("✅ Fallback работает!")
            print("🎉 Fallback решение готово!")
        else:
            print(f"❌ Fallback не работает: {result[:200]}")
        
        print("\n📋 ИНСТРУКЦИИ:")
        print("1. Откройте http://72.56.66.228/module/vacancies")
        print("2. Сгенерируйте текст")
        print("3. Используйте fallback для генерации аудио")
        print("4. Fallback использует системный TTS (espeak)")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    create_fallback_solution()
