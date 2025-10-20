import requests
import time
import os
from typing import Optional, List, Dict, Any
from config import Config
import io
import ssl
import urllib3
import tempfile

# Отключаем предупреждения SSL для старых версий
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ElevenLabsClient:
    def __init__(self, api_key: str = None):
        # Ключ берём из аргумента или окружения, не храним в коде
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["xi-api-key"] = self.api_key
        
        # Доступные модели ElevenLabs
        self.available_models = {
            "eleven_multilingual_v2": {
                "name": "Eleven Multilingual v2",
                "description": "Excels in stability, language diversity, and accent accuracy. Supports 29 languages. Recommended for most use cases.",
                "languages": 29
            },
            "eleven_flash_v2_5": {
                "name": "Eleven Flash v2.5", 
                "description": "Ultra-low latency. Supports 32 languages. Faster model, 50% lower price per character.",
                "languages": 32
            },
            "eleven_turbo_v2_5": {
                "name": "Eleven Turbo v2.5",
                "description": "Good balance of quality and latency. Ideal for developer use cases where speed is crucial. Supports 32 languages.",
                "languages": 32
            }
        }
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Получение списка доступных голосов
        """
        if not self.api_key:
            print("ElevenLabs API key not configured")
            return []

        try:
            # Используем более мягкие настройки SSL
            response = requests.get(
                f"{self.base_url}/voices", 
                headers=self.headers,
                verify=False,  # Отключаем проверку SSL для совместимости
                timeout=30
            )
            response.raise_for_status()
            
            voices_data = response.json()
            return [
                {
                    "voice_id": voice["voice_id"],
                    "name": voice["name"],
                    "category": voice.get("category", ""),
                    "description": voice.get("description", ""),
                    "preview_url": voice.get("preview_url", "")
                }
                for voice in voices_data.get("voices", [])
            ]
        except Exception as e:
            print(f"Error getting voices: {e}")
            return []
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Получение списка доступных моделей
        """
        return self.available_models
    
    def text_to_speech(self, text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb", 
                      model_id: str = "eleven_multilingual_v2",
                      stability: float = 0.5, similarity_boost: float = 0.5,
                      max_retries: int = 3) -> Optional[bytes]:
        """
        Преобразование текста в речь с выбором модели
        """
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            },
            "output_format": "mp3_44100_128"
        }
        
        if not self.api_key:
            raise Exception("ElevenLabs API key not configured")

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url, 
                    json=data, 
                    headers=self.headers,
                    verify=False,
                    timeout=60
                )
                response.raise_for_status()
                
                return response.content
                
            except Exception as e:
                print(f"ElevenLabs attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2)
        
        return None
    
    def save_audio_to_cloud(self, audio_data: bytes, filename: str) -> str:
        """
        Сохранение аудио в облачное хранилище
        """
        from api.cloud_storage import CloudStorageClient
        
        cloud_client = CloudStorageClient()
        
        # Создаем путь с датой
        from datetime import datetime
        date_path = datetime.now().strftime("%Y/%m/%d")
        full_path = f"audio/{date_path}/{filename}"
        
        return cloud_client.upload_file(audio_data, full_path, content_type="audio/mpeg")
    
    def generate_audio(self, text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb", 
                      model_id: str = "eleven_multilingual_v2") -> Optional[str]:
        """
        Генерация аудио с выбором модели и голоса
        """
        print(f"🎵 Генерация аудио для текста: {text[:50]}...")
        
        # Проверяем доступность API
        if not self.api_key or not self.test_connection():
            print("⚠️ ElevenLabs API недоступен, используем fallback")
            return self._create_audio_placeholder(text)
        
        try:
            # Пробуем реальный API
            audio_data = self.text_to_speech(text, voice_id, model_id)
            if audio_data:
                # Сохраняем аудио в файл и возвращаем URL
                import os
                import uuid
                
                # Создаем директорию для аудио файлов
                audio_dir = "static/audio"
                os.makedirs(audio_dir, exist_ok=True)
                
                # Генерируем уникальное имя файла
                filename = f"audio_{uuid.uuid4().hex}.mp3"
                filepath = os.path.join(audio_dir, filename)
                
                # Сохраняем аудио
                with open(filepath, 'wb') as f:
                    f.write(audio_data)
                
                # Устанавливаем правильные права доступа
                os.chmod(filepath, 0o644)
                
                print(f"✅ Аудио сохранено: {filepath}")
                return f"/static/audio/{filename}"
            
        except Exception as e:
            print(f"❌ ElevenLabs API ошибка: {e}")
        
        # Fallback: создаем заглушку аудио
        print("🔄 Используем fallback аудио")
        return self._create_audio_placeholder(text)
    
    def _create_audio_placeholder(self, text: str) -> str:
        """Создает заглушку аудио для демонстрации"""
        import os
        import uuid
        
        # Создаем директорию для аудио файлов
        audio_dir = "static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        
        # Генерируем уникальное имя файла
        filename = f"placeholder_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(audio_dir, filename)
        
        # Создаем минимальный валидный MP3 файл с правильным заголовком
        # MP3 заголовок для 128kbps, 44.1kHz, моно
        mp3_header = bytes([
            0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])
        
        # Создаем данные для ~5 секунд тишины
        audio_data = mp3_header * 500  # ~5 секунд
        
        # Сохраняем файл
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        
        # Устанавливаем правильные права доступа
        os.chmod(filepath, 0o644)
        
        print(f"Создана заглушка аудио: {filepath} (размер: {len(audio_data)} байт)")
        return f"/static/audio/{filename}"
    
    def _audio_to_base64(self, audio_data: bytes) -> str:
        """Конвертирует аудио данные в base64 для воспроизведения в браузере"""
        import base64
        return base64.b64encode(audio_data).decode('utf-8')

    def generate_speech_for_video(self, text: str, voice_id: str) -> Optional[str]:
        """
        Полный пайплайн: текст -> аудио -> сохранение в облако
        """
        try:
            # Генерируем аудио
            audio_data = self.text_to_speech(text, voice_id)
            if not audio_data:
                return None
            
            # Сохраняем в облако
            filename = f"speech_{int(time.time())}.mp3"
            audio_url = self.save_audio_to_cloud(audio_data, filename)
            
            return audio_url
            
        except Exception as e:
            print(f"Error in speech generation pipeline: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Проверка подключения к ElevenLabs API
        """
        if not self.api_key:
            return False
        try:
            response = requests.get(
                f"{self.base_url}/voices", 
                headers=self.headers,
                verify=False,
                timeout=10
            )
            print(f"ElevenLabs API response: {response.status_code}")
            if response.status_code == 200:
                print("ElevenLabs API работает!")
                return True
            else:
                print(f"ElevenLabs API ошибка: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"ElevenLabs API недоступен: {e}")
            return False
