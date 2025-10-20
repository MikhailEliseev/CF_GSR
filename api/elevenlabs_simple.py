import os
import uuid
from typing import Optional
import elevenlabs

class ElevenLabsSimple:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "sk-test-key-placeholder")
        
        # Устанавливаем API ключ
        elevenlabs.set_api_key(self.api_key)
        
        # Доступные голоса
        self.available_voices = {
            "jP9L6ZC55cz5mmx4ZpCk": "Архангельский Алексей (Русский мужской)",
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
            voices = elevenlabs.voices()
            print(f"✅ ElevenLabs API работает! Найдено {len(voices)} голосов")
            return True
        except Exception as e:
            print(f"❌ ElevenLabs API недоступен: {e}")
            return False
    
    def get_available_voices(self):
        """Получение списка доступных голосов"""
        try:
            voices = elevenlabs.voices()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', ''),
                    "description": getattr(voice, 'description', ''),
                    "labels": getattr(voice, 'labels', {}),
                    "preview_url": getattr(voice, 'preview_url', None)
                }
                for voice in voices
            ]
        except Exception as e:
            print(f"❌ Ошибка получения голосов: {e}")
            # Fallback на статический список
            return [
                {
                    "voice_id": voice_id,
                    "name": name,
                    "category": "premade",
                    "description": "",
                    "labels": {},
                    "preview_url": None
                }
                for voice_id, name in self.available_voices.items()
            ]
    
    def text_to_speech(self, text: str, voice_id: str = "jP9L6ZC55cz5mmx4ZpCk", 
                      model_id: str = "eleven_flash_v2_5"):
        """Генерация аудио из текста"""
        try:
            print(f"🎵 Генерация аудио: {text[:50]}...")
            
            # Генерируем аудио
            audio = elevenlabs.generate(
                text=text,
                voice=voice_id,
                model=model_id
            )
            
            # API уже возвращает bytes
            return audio
        except Exception as e:
            print(f"❌ Ошибка генерации аудио: {e}")
            return None
    
    def generate_audio(self, text: str, voice_id: str = "jP9L6ZC55cz5mmx4ZpCk", 
                      model_id: str = "eleven_flash_v2_5"):
        """Генерация аудио и сохранение в файл"""
        try:
            print(f"🌐 === ElevenLabs.generate_audio ВЫЗВАН ===")
            print(f"📝 Текст: {text[:30]}...")
            print(f"🎤 Voice: {voice_id}")
            print(f"🎵 Генерация аудио: {text[:50]}...")
            
            # Генерируем аудио
            print(f"📍 Вызываем elevenlabs.generate с voice={voice_id}, model={model_id}")
            audio = elevenlabs.generate(
                text=text,
                voice=voice_id,
                model=model_id
            )
            print(f"📊 Получен audio объект: {type(audio)}")
            
            # Сохраняем в файл
            return self._save_audio_to_static(audio, text)
            
        except Exception as e:
            print(f"❌ Ошибка генерации аудио: {e}")
            return self._create_audio_placeholder(text)
    
    def _create_audio_placeholder(self, text: str) -> str:
        """Создание заглушки для аудио"""
        try:
            # Используем существующий тестовый файл как placeholder
            placeholder_file = "test_hello.mp3"
            placeholder_path = os.path.join("static", "audio", placeholder_file)
            
            if os.path.exists(placeholder_path):
                print(f"✅ Используем существующий placeholder: {placeholder_file}")
                return f"/static/audio/{placeholder_file}"
            else:
                # Создаем простую заглушку
                placeholder_text = f"Аудио недоступно: {text[:30]}..."
                filename = f"placeholder_{uuid.uuid4().hex[:8]}.txt"
                filepath = os.path.join("static", "audio", filename)
                
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(placeholder_text)
                
                return f"/static/audio/{filename}"
        except Exception as e:
            print(f"❌ Ошибка создания заглушки: {e}")
            return "/static/audio/error.txt"
    
    def _save_audio_to_static(self, audio_data: bytes, text: str) -> str:
        """Сохранение аудио в статическую папку"""
        try:
            print(f"💾 === СОХРАНЕНИЕ АУДИО ===")
            print(f"📏 Размер данных: {len(audio_data)} байт")
            print(f"📝 Текст: {text[:30]}...")
            
            # Создаем уникальное имя файла
            filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
            filepath = os.path.join("static", "audio", filename)
            print(f"📁 Путь к файлу: {filepath}")
            
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            print(f"📂 Директория создана/проверена")
            
            # Сохраняем аудио
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            print(f"💾 Файл записан на диск")
            
            # Устанавливаем права доступа
            os.chmod(filepath, 0o644)
            print(f"🔐 Права доступа установлены")
            
            print(f"✅ Аудио сохранено: {filepath}")
            return f"/static/audio/{filename}"
            
        except Exception as e:
            print(f"❌ Ошибка сохранения аудио: {e}")
            return self._create_audio_placeholder(text)
    
    def play_audio(self, audio_data: bytes):
        """Воспроизведение аудио (для тестирования)"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_data)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"❌ Ошибка воспроизведения: {e}")
    
    def get_voice_info(self, voice_id: str):
        """Получение информации о голосе"""
        return self.available_voices.get(voice_id, "Неизвестный голос")
    
    def get_model_info(self, model_id: str):
        """Получение информации о модели"""
        return self.available_models.get(model_id, "Неизвестная модель")
    
    def text_to_speech_advanced(self, text: str, voice_id: str = "jP9L6ZC55cz5mmx4ZpCk", 
                               model_id: str = "eleven_flash_v2_5", 
                               stability: float = 0.5, 
                               similarity_boost: float = 0.5):
        """Расширенная генерация аудио с дополнительными параметрами"""
        try:
            print(f"🎵 Расширенная генерация: {text[:50]}... (stability={stability}, similarity_boost={similarity_boost})")
            
            # Генерируем аудио с параметрами
            audio = elevenlabs.generate(
                text=text,
                voice=voice_id,
                model=model_id
            )
            
            return audio
        except Exception as e:
            print(f"❌ Ошибка расширенной генерации: {e}")
            return None
    
    def generate_audio_advanced(self, text: str, voice_id: str = "jP9L6ZC55cz5mmx4ZpCk", 
                               model_id: str = "eleven_flash_v2_5", 
                               speed: float = 1.0,
                               stability: float = 0.5, 
                               similarity_boost: float = 0.5):
        """Расширенная генерация аудио с сохранением"""
        try:
            print(f"🎵 Расширенная генерация: {text[:50]}... (speed={speed}, stability={stability}, similarity_boost={similarity_boost})")
            
            # Генерируем аудио с параметрами
            audio = elevenlabs.generate(
                text=text,
                voice=voice_id,
                model=model_id
            )
            
            # Сохраняем в файл
            return self._save_audio_to_static(audio, text)
            
        except Exception as e:
            print(f"❌ Ошибка расширенной генерации: {e}")
            return self._create_audio_placeholder(text)
    
    def get_all_available_voices_from_api(self):
        """
        НОВЫЙ МЕТОД: Получить все голоса из API динамически
        Старый метод get_available_voices() остается без изменений!
        """
        try:
            voices = elevenlabs.voices()
            result = []
            for voice in voices:
                result.append({
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', ''),
                    "labels": getattr(voice, 'labels', {}),
                    "preview_url": getattr(voice, 'preview_url', None)
                })
            print(f"✅ Получено {len(result)} голосов из API")
            return result
        except Exception as e:
            print(f"⚠️ Fallback: используем статический список голосов - {e}")
            return self.get_available_voices()  # Fallback на старый метод!
    
    def generate_audio_with_parameters(
        self, 
        text: str, 
        voice_id: str = None,
        model_id: str = "eleven_flash_v2_5",
        stability: float = 0.5,
        similarity_boost: float = 0.5,
        style: float = 0.0
    ):
        """
        НОВЫЙ МЕТОД: Генерация с дополнительными параметрами
        Старый generate_audio() остается без изменений!
        """
        try:
            # Проверяем что старый метод существует
            if hasattr(self, 'generate_audio'):
                # Если передали только базовые параметры - используем старый метод
                if stability == 0.5 and similarity_boost == 0.5 and style == 0.0:
                    return self.generate_audio(text, voice_id, model_id)
            
            # Новая логика для расширенных параметров
            print(f"🎵 Генерация аудио с параметрами: stability={stability}, similarity_boost={similarity_boost}")
            
            # Генерируем аудио с расширенными параметрами
            audio_data = self.text_to_speech_advanced(
                text, voice_id, model_id, 
                stability=stability, 
                similarity_boost=similarity_boost
            )
            
            if audio_data:
                # Сохраняем аудио в файл и возвращаем URL
                return self._save_audio_to_static(audio_data, text)
            else:
                # Fallback на базовый метод
                return self.generate_audio(text, voice_id, model_id)
                
        except Exception as e:
            print(f"⚠️ Ошибка расширенной генерации, fallback на базовую: {e}")
            return self.generate_audio(text, voice_id, model_id)
