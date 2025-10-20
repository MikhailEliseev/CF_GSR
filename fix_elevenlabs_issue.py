#!/usr/bin/env python3
"""
Исправление проблемы с ElevenLabs
"""

import paramiko
import json

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def fix_elevenlabs():
    """Исправляем проблему с ElevenLabs"""
    print("🔧 Исправляем проблему с ElevenLabs...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Добавляем fallback для ElevenLabs
        print("\n1️⃣ Добавляем fallback для ElevenLabs...")
        
        fallback_code = '''
# Добавляем в routes/vacancies.py fallback для ElevenLabs
import os
import tempfile
import subprocess

def generate_audio_fallback(text, output_path):
    """Fallback генерация аудио через системный TTS"""
    try:
        # Используем espeak для генерации аудио
        temp_file = tempfile.mktemp(suffix=".wav")
        
        # Генерируем аудио через espeak
        cmd = ["espeak", "-s", "150", "-v", "ru", "-w", temp_file, text]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(temp_file):
            # Конвертируем в MP3 если нужно
            if output_path.endswith('.mp3'):
                mp3_file = tempfile.mktemp(suffix=".mp3")
                convert_cmd = ["ffmpeg", "-i", temp_file, "-acodec", "mp3", mp3_file]
                convert_result = subprocess.run(convert_cmd, capture_output=True, text=True)
                
                if convert_result.returncode == 0:
                    os.rename(mp3_file, output_path)
                    os.unlink(temp_file)
                    return True
                else:
                    os.rename(temp_file, output_path)
                    return True
            else:
                os.rename(temp_file, output_path)
                return True
        else:
            print(f"Ошибка espeak: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Ошибка fallback: {e}")
        return False
'''
        
        # 2. Обновляем ElevenLabs сервис с fallback
        print("\n2️⃣ Обновляем ElevenLabs сервис...")
        
        updated_service = '''
import requests
import json
import os
import tempfile
import subprocess
from typing import Optional

class ElevenLabsService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def generate_audio(self, text: str, voice_id: str = None, output_path: str = None) -> Optional[str]:
        """Генерирует аудио с fallback"""
        try:
            # Пробуем ElevenLabs API
            if self._try_elevenlabs_api(text, voice_id, output_path):
                return output_path
        except Exception as e:
            print(f"ElevenLabs API недоступен: {e}")
        
        # Fallback на системный TTS
        print("Используем fallback TTS...")
        return self._generate_audio_fallback(text, output_path)
    
    def _try_elevenlabs_api(self, text: str, voice_id: str, output_path: str) -> bool:
        """Пробует использовать ElevenLabs API"""
        try:
            # Получаем голоса если не указан
            if not voice_id:
                voices_response = requests.get(
                    f"{self.base_url}/voices",
                    headers={"xi-api-key": self.api_key},
                    timeout=10
                )
                if voices_response.status_code == 200:
                    voices = voices_response.json()
                    if voices.get('voices'):
                        voice_id = voices['voices'][0]['voice_id']
                    else:
                        return False
                else:
                    return False
            
            # Генерируем аудио
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"ElevenLabs API ошибка: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"ElevenLabs API исключение: {e}")
            return False
    
    def _generate_audio_fallback(self, text: str, output_path: str) -> Optional[str]:
        """Fallback генерация аудио"""
        try:
            temp_file = tempfile.mktemp(suffix=".wav")
            
            # Используем espeak
            cmd = ["espeak", "-s", "150", "-v", "ru", "-w", temp_file, text]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(temp_file):
                if output_path.endswith('.mp3'):
                    # Конвертируем в MP3
                    mp3_file = tempfile.mktemp(suffix=".mp3")
                    convert_cmd = ["ffmpeg", "-i", temp_file, "-acodec", "mp3", "-y", mp3_file]
                    convert_result = subprocess.run(convert_cmd, capture_output=True, text=True)
                    
                    if convert_result.returncode == 0:
                        os.rename(mp3_file, output_path)
                        os.unlink(temp_file)
                        return output_path
                    else:
                        os.rename(temp_file, output_path)
                        return output_path
                else:
                    os.rename(temp_file, output_path)
                    return output_path
            else:
                print(f"Ошибка espeak: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Ошибка fallback: {e}")
            return None
'''
        
        # Записываем обновленный сервис
        stdin, stdout, stderr = ssh.exec_command("cat > /root/services/elevenlabs_service.py << 'EOF'\n" + updated_service + "\nEOF")
        stdout.read()
        print("✅ Обновлен ElevenLabs сервис с fallback")
        
        # 3. Устанавливаем espeak на сервере
        print("\n3️⃣ Устанавливаем espeak...")
        stdin, stdout, stderr = ssh.exec_command("apt-get update && apt-get install -y espeak ffmpeg")
        install_result = stdout.read().decode()
        print("Результат установки:")
        print(install_result[:500])
        
        # 4. Перезапускаем сервер
        print("\n4️⃣ Перезапускаем сервер...")
        ssh.exec_command("pkill -f python.*app")
        time.sleep(2)
        ssh.exec_command("cd /root && nohup python3 app.py > server.log 2>&1 &")
        time.sleep(3)
        
        # Проверяем что сервер запустился
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep python.*app | grep -v grep")
        processes = stdout.read().decode()
        if processes:
            print("✅ Сервер перезапущен")
        else:
            print("❌ Сервер не запустился")
        
        print("\n🎉 Исправление завершено!")
        print("Теперь ElevenLabs будет использовать fallback TTS если API недоступен")
        
    except Exception as e:
        print(f"❌ Ошибка исправления: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_elevenlabs()
