import os
import assemblyai as aai
from typing import Optional
import time
import requests

class AssemblyAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ASSEMBLYAI_API_KEY', 'test-key-placeholder')
        if not self.api_key or self.api_key == 'test-key-placeholder':
            print("⚠️ AssemblyAI API ключ не настроен, используем заглушку")
        else:
            aai.settings.api_key = self.api_key

    def transcribe_audio_url(self, audio_url: str, language_code: str = "ru") -> str:
        """Транскрипция аудио с обработкой таймаутов"""
        try:
            # Проверяем API ключ
            if not self.api_key or self.api_key == 'test-key-placeholder':
                return f"Демо-транскрипция для {audio_url[:50]}... (AssemblyAI API ключ не настроен)"
            
            print(f"🎤 Транскрибирую аудио: {audio_url[:50]}...")
            
            # Настраиваем конфигурацию с таймаутом
            config = aai.TranscriptionConfig(
                language_code=language_code, 
                punctuate=True, 
                format_text=True,
                auto_highlights=True,
                sentiment_analysis=True
            )
            
            transcriber = aai.Transcriber(config=config)
            
            # Транскрибируем с таймаутом
            transcript = transcriber.transcribe(audio_url)
            
            # Ждем завершения с таймаутом
            timeout = 300  # 5 минут для длинных видео
            start_time = time.time()
            
            while transcript.status not in [aai.TranscriptStatus.completed, aai.TranscriptStatus.error]:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Транскрипция превысила время ожидания")
                
                time.sleep(2)
                print(f"⏳ Статус транскрипции: {transcript.status}")
            
            if transcript.status == aai.TranscriptStatus.error:
                raise RuntimeError(f"AssemblyAI error: {transcript.error}")
            
            if transcript.status == aai.TranscriptStatus.completed:
                print("✅ Транскрипция завершена успешно")
                return transcript.text
            else:
                raise RuntimeError(f"Неожиданный статус транскрипции: {transcript.status}")
                
        except TimeoutError as e:
            print(f"⏰ Таймаут транскрипции: {e}")
            return f"Ошибка таймаута: {str(e)}"
        except Exception as e:
            print(f"❌ Ошибка транскрипции: {e}")
            return f"Ошибка транскрипции: {str(e)}"

    def transcribe_video_url(self, video_url: str, language_code: str = "ru") -> str:
        """Транскрипция видео"""
        return self.transcribe_audio_url(video_url, language_code)

    def test_connection(self) -> bool:
        """Тестирует подключение к AssemblyAI"""
        try:
            if not self.api_key or self.api_key == 'test-key-placeholder':
                print("⚠️ AssemblyAI API ключ не настроен")
                return False
            
            # Простой тест подключения
            response = requests.get("https://api.assemblyai.com/v2/transcript", 
                                 headers={"authorization": self.api_key}, 
                                 timeout=10)
            return response.status_code in [200, 401]  # 401 тоже нормально для теста
        except Exception as e:
            print(f"❌ Ошибка тестирования AssemblyAI: {e}")
            return False
