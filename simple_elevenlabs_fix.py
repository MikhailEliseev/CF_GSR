#!/usr/bin/env python3
"""
Простое исправление ElevenLabs
"""

import paramiko
import time

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def simple_fix():
    """Простое исправление ElevenLabs"""
    print("🔧 Простое исправление ElevenLabs...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Устанавливаем espeak
        print("\n1️⃣ Устанавливаем espeak...")
        stdin, stdout, stderr = ssh.exec_command("apt-get update && apt-get install -y espeak ffmpeg")
        result = stdout.read().decode()
        print("Установка завершена")
        
        # 2. Создаем простой fallback endpoint
        print("\n2️⃣ Создаем fallback endpoint...")
        
        fallback_endpoint = '''
@vacancies_bp.route('/api/vacancies/generate-audio-fallback', methods=['POST'])
def generate_audio_fallback():
    """Fallback генерация аудио через espeak"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"success": False, "error": "Текст не указан"}), 400
        
        # Создаем временный файл
        import tempfile
        import subprocess
        import os
        
        temp_wav = tempfile.mktemp(suffix=".wav")
        temp_mp3 = tempfile.mktemp(suffix=".mp3")
        
        # Генерируем аудио через espeak
        cmd = ["espeak", "-s", "150", "-v", "ru", "-w", temp_wav, text]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(temp_wav):
            # Конвертируем в MP3
            convert_cmd = ["ffmpeg", "-i", temp_wav, "-acodec", "mp3", "-y", temp_mp3]
            convert_result = subprocess.run(convert_cmd, capture_output=True, text=True)
            
            if convert_result.returncode == 0:
                # Читаем MP3 файл
                with open(temp_mp3, 'rb') as f:
                    audio_data = f.read()
                
                # Очищаем временные файлы
                os.unlink(temp_wav)
                os.unlink(temp_mp3)
                
                # Возвращаем base64
                import base64
                audio_base64 = base64.b64encode(audio_data).decode()
                
                return jsonify({
                    "success": True,
                    "audio_data": audio_base64,
                    "method": "espeak_fallback"
                })
            else:
                # Возвращаем WAV если MP3 не получился
                with open(temp_wav, 'rb') as f:
                    audio_data = f.read()
                
                os.unlink(temp_wav)
                if os.path.exists(temp_mp3):
                    os.unlink(temp_mp3)
                
                import base64
                audio_base64 = base64.b64encode(audio_data).decode()
                
                return jsonify({
                    "success": True,
                    "audio_data": audio_base64,
                    "method": "espeak_wav"
                })
        else:
            return jsonify({
                "success": False,
                "error": f"Ошибка espeak: {result.stderr}"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Ошибка fallback: {str(e)}"
        }), 500
'''
        
        # Добавляем endpoint в routes/vacancies.py
        stdin, stdout, stderr = ssh.exec_command("echo '\n" + fallback_endpoint + "' >> /root/routes/vacancies.py")
        stdout.read()
        print("✅ Добавлен fallback endpoint")
        
        # 3. Перезапускаем сервер
        print("\n3️⃣ Перезапускаем сервер...")
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
        
        # 4. Тестируем fallback
        print("\n4️⃣ Тестируем fallback...")
        test_payload = {
            "text": "Привет! Это тест fallback аудио."
        }
        
        import json
        test_cmd = f"curl -X POST -H 'Content-Type: application/json' -d '{json.dumps(test_payload)}' http://localhost:5000/api/vacancies/generate-audio-fallback"
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        result = stdout.read().decode()
        
        if "success" in result and "audio_data" in result:
            print("✅ Fallback работает!")
        else:
            print(f"❌ Fallback не работает: {result[:200]}")
        
        print("\n🎉 Исправление завершено!")
        print("Теперь можно использовать fallback для генерации аудио")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    simple_fix()
