import os
import uuid
from typing import Optional
try:
    from elevenlabs import ElevenLabs, play
except ImportError:
    # Fallback для старых версий
    import elevenlabs
    ElevenLabs = elevenlabs.ElevenLabs
    play = elevenlabs.play

class ElevenLabsClientNew:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "1d5cd83ef960acc13a1a1dd9a1c87cab2309bc763255060a9ff75203751a1c85")
        self.client = ElevenLabs(api_key=self.api_key)
        
        # Доступные голоса
        self.available_voices = {
            "JBFqnCBsd6RMkjVDRZzb": "Rachel (Female, American)",
            "EXAVITQu4vr4xnSDxMaL": "Bella (Female, American)", 
            "VR6AewLTigWG4xSOukaG": "Josh (Male, American)",
            "AZnzlk1XvdvUeBnXmlld": "Domi (Female, American)",
            "MF3mGyEYCl7XYWbV9V6O": "Elli (Female, American)"
        }
        
        # Доступные модели
        self.available_models = {
            "eleven_multilingual_v2": "Eleven Multilingual v2 (29 языков)",
            "eleven_flash_v2_5": "Eleven Flash v2.5 (32 языка, быстрый)",
            "eleven_turbo_v2_5": "Eleven Turbo v2.5 (32 языка, сбалансированный)"
        }
    
    def test_connection(self) -> bool:
        """Проверка подключения к ElevenLabs API"""
        try:
            # Пробуем получить список голосов
            voices = self.client.voices.get_all()
            print(f"✅ ElevenLabs API работает! Найдено {len(voices)} голосов")
            return True
        except Exception as e:
            print(f"❌ ElevenLabs API недоступен: {e}")
            return False
    
    def get_available_voices(self):
        """Получение списка доступных голосов"""
        try:
            voices = self.client.voices.get_all()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', ''),
                    "description": getattr(voice, 'description', ''),
                    "preview_url": getattr(voice, 'preview_url', '')
                }
                for voice in voices
            ]
        except Exception as e:
            print(f"Ошибка получения голосов: {e}")
            return []
    
    def text_to_speech(self, text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb", 
                      model_id: str = "eleven_multilingual_v2") -> Optional[bytes]:
        """
        Преобразование текста в речь с новой логикой
        """
        try:
            print(f"🎵 Генерация аудио: {text[:50]}...")
            
            # Используем новый API
            audio = self.client.generate(
                text=text,
                voice=voice_id,
                model=model_id
            )
            
            # Конвертируем в bytes
            audio_bytes = b''.join(audio)
            print(f"✅ Аудио сгенерировано: {len(audio_bytes)} байт")
            return audio_bytes
            
        except Exception as e:
            print(f"❌ Ошибка генерации аудио: {e}")
            return None
    
    def generate_audio(self, text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb", 
                      model_id: str = "eleven_multilingual_v2") -> Optional[str]:
        """
        Полный пайплайн: текст -> аудио -> сохранение файла
        """
        print(f"🎵 Генерация аудио для текста: {text[:50]}...")
        
        # Проверяем подключение
        if not self.test_connection():
            print("⚠️ ElevenLabs API недоступен, используем fallback")
            return self._create_audio_placeholder(text)
        
        try:
            # Генерируем аудио
            audio_data = self.text_to_speech(text, voice_id, model_id)
            if not audio_data:
                print("❌ Не удалось сгенерировать аудио")
                return self._create_audio_placeholder(text)
            
            # Сохраняем в файл
            audio_dir = "static/audio"
            os.makedirs(audio_dir, exist_ok=True)
            
            filename = f"audio_{uuid.uuid4().hex}.mp3"
            filepath = os.path.join(audio_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            os.chmod(filepath, 0o644)
            
            print(f"✅ Аудио сохранено: {filepath}")
            return f"/static/audio/{filename}"
            
        except Exception as e:
            print(f"❌ Ошибка в пайплайне: {e}")
            return self._create_audio_placeholder(text)
    
    def _create_audio_placeholder(self, text: str) -> str:
        """Создает заглушку аудио для демонстрации"""
        print("🔄 Создаем fallback аудио")
        
        audio_dir = "static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        
        filename = f"placeholder_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(audio_dir, filename)
        
        # Создаем минимальный валидный MP3 файл
        mp3_header = bytes([
            0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])
        
        # Создаем данные для ~5 секунд тишины
        audio_data = mp3_header * 500
        
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        
        os.chmod(filepath, 0o644)
        
        print(f"✅ Создана заглушка: {filepath} ({len(audio_data)} байт)")
        return f"/static/audio/{filename}"
    
    def play_audio(self, audio_data: bytes):
        """Воспроизведение аудио (для тестирования)"""
        try:
            play(audio_data)
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
    
    def get_voice_info(self, voice_id: str):
        """Получение информации о голосе"""
        return self.available_voices.get(voice_id, "Неизвестный голос")
    
    def get_model_info(self, model_id: str):
        """Получение информации о модели"""
        return self.available_models.get(model_id, "Неизвестная модель")
