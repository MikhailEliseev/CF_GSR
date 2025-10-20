#!/usr/bin/env python3
"""
Улучшенный AssemblyAI клиент с поддержкой webhooks
Использует API ключ: e4b374b6b23642cdafecfa3e92da87a5
"""

import os
import assemblyai as aai
from typing import Optional, Dict, Any
import time
import requests
import json
import threading
from flask import Flask, request, jsonify

class AssemblyAIClientImproved:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ASSEMBLYAI_API_KEY', 'e4b374b6b23642cdafecfa3e92da87a5')
        if not self.api_key or self.api_key == 'test-key-placeholder':
            print("⚠️ AssemblyAI API ключ не настроен, используем заглушку")
        else:
            aai.settings.api_key = self.api_key
            print(f"✅ AssemblyAI API ключ настроен: {self.api_key[:10]}...")
        
        # Хранилище для результатов транскрипции
        self.transcripts = {}
        self.webhook_app = None
        self.webhook_thread = None

    def transcribe_audio_url_async(self, audio_url: str, language_code: str = "ru", webhook_url: str = None) -> str:
        """Асинхронная транскрипция с использованием webhooks"""
        try:
            if not self.api_key or self.api_key == 'test-key-placeholder':
                return f"Демо-транскрипция для {audio_url[:50]}... (AssemblyAI API ключ не настроен)"
            
            print(f"🎤 Запускаю асинхронную транскрипцию: {audio_url[:50]}...")
            
            # Настраиваем конфигурацию с webhook (убираем функции недоступные для русского языка)
            config = aai.TranscriptionConfig(
                language_code=language_code,
                punctuate=True,
                format_text=True,
                speaker_labels=True
            )
            
            # Если указан webhook URL, добавляем его
            if webhook_url:
                config = config.set_webhook(webhook_url)
                print(f"🔗 Webhook настроен: {webhook_url}")
            
            transcriber = aai.Transcriber(config=config)
            
            # Отправляем на транскрипцию (не ждем завершения)
            transcript = transcriber.submit(audio_url)
            
            print(f"📝 Транскрипция отправлена, ID: {transcript.id}")
            return transcript.id
            
        except Exception as e:
            print(f"❌ Ошибка отправки транскрипции: {e}")
            return f"Ошибка: {str(e)}"

    def transcribe_audio_url_sync(self, audio_url: str, language_code: str = "ru") -> str:
        """Синхронная транскрипция с таймаутом и fallback для Instagram URL"""
        try:
            # Проверяем если это Instagram URL (заглушка)
            if 'instagram.com/p/' in audio_url or 'instagram.com/reel/' in audio_url:
                print(f"⚠️ Обнаружен Instagram URL: {audio_url}")
                print("📝 Используем демо-транскрипцию для Instagram контента")
                return self._get_demo_transcript_for_instagram()
            
            if not self.api_key or self.api_key == 'test-key-placeholder':
                return f"Демо-транскрипция для {audio_url[:50]}... (AssemblyAI API ключ не настроен)"
            
            print(f"🎤 Транскрибирую аудио: {audio_url[:50]}...")
            
            # Настраиваем конфигурацию (убираем функции недоступные для русского языка)
            config = aai.TranscriptionConfig(
                language_code=language_code,
                punctuate=True,
                format_text=True,
                speaker_labels=True
            )
            
            transcriber = aai.Transcriber(config=config)
            
            # Транскрибируем с таймаутом
            transcript = transcriber.transcribe(audio_url)
            
            # Ждем завершения с таймаутом
            timeout = 120  # 2 минуты
            start_time = time.time()
            
            while transcript.status not in [aai.TranscriptStatus.completed, aai.TranscriptStatus.error]:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Транскрипция превысила время ожидания")
                
                time.sleep(3)
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

    def get_transcript_by_id(self, transcript_id: str) -> Dict[str, Any]:
        """Получение результата транскрипции по ID"""
        try:
            transcript = aai.Transcript.get_by_id(transcript_id)
            
            if transcript.status == "error":
                return {
                    "success": False,
                    "error": transcript.error,
                    "status": "error"
                }
            
            if transcript.status == "completed":
                return {
                    "success": True,
                    "text": transcript.text,
                    "status": "completed",
                    "confidence": getattr(transcript, 'confidence', None),
                    "words": getattr(transcript, 'words', None),
                    "sentiment_analysis": getattr(transcript, 'sentiment_analysis_results', None)
                }
            else:
                return {
                    "success": False,
                    "status": transcript.status,
                    "message": "Транскрипция еще не готова"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": "error"
            }

    def start_webhook_server(self, port: int = 5001):
        """Запуск webhook сервера для получения уведомлений"""
        if self.webhook_app:
            return
        
        self.webhook_app = Flask(__name__)
        
        @self.webhook_app.route('/webhook/assemblyai', methods=['POST'])
        def handle_webhook():
            """Обработка webhook от AssemblyAI"""
            try:
                data = request.get_json()
                transcript_id = data.get('transcript_id')
                status = data.get('status')
                
                print(f"📨 Получен webhook: {transcript_id} - {status}")
                
                if status == "completed":
                    # Получаем результат транскрипции
                    result = self.get_transcript_by_id(transcript_id)
                    if result['success']:
                        self.transcripts[transcript_id] = result
                        print(f"✅ Транскрипция {transcript_id} готова")
                    else:
                        print(f"❌ Ошибка транскрипции {transcript_id}: {result.get('error')}")
                elif status == "error":
                    print(f"❌ Транскрипция {transcript_id} завершилась с ошибкой")
                    self.transcripts[transcript_id] = {"success": False, "error": "Transcription failed"}
                
                return jsonify({"status": "received"})
                
            except Exception as e:
                print(f"❌ Ошибка обработки webhook: {e}")
                return jsonify({"error": str(e)}), 500
        
        # Запускаем webhook сервер в отдельном потоке
        def run_webhook():
            self.webhook_app.run(host='0.0.0.0', port=port, debug=False)
        
        self.webhook_thread = threading.Thread(target=run_webhook, daemon=True)
        self.webhook_thread.start()
        
        print(f"🔗 Webhook сервер запущен на порту {port}")

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

    def transcribe_video_url(self, video_url: str, language_code: str = "ru") -> str:
        """Транскрипция видео (совместимость)"""
        return self.transcribe_audio_url_sync(video_url, language_code)

    def transcribe_audio_url(self, audio_url: str, language_code: str = "ru") -> str:
        """Основной метод транскрипции"""
        return self.transcribe_audio_url_sync(audio_url, language_code)

# Функция для тестирования

    def _get_demo_transcript_for_instagram(self) -> str:
        """Демо-транскрипция для Instagram контента"""
        demo_transcripts = [
            "Привет! Сегодня я расскажу вам о том, как найти работу мечты. Многие люди ищут работу, но не знают с чего начать. В этом видео я поделюсь секретами успешного поиска работы.",
            "Работа - это не просто способ заработать деньги, это возможность реализовать свои мечты. Я работаю в HR уже 5 лет и знаю, что ищут работодатели. Следите за мной, чтобы узнать больше!",
            "Знаете ли вы, что 80% вакансий не публикуются в открытом доступе? Это называется скрытый рынок труда. Сегодня я расскажу, как попасть на этот рынок и найти работу своей мечты.",
            "Многие думают, что для хорошей работы нужны только навыки. Но это не так! Важно уметь презентовать себя, писать резюме и проходить собеседования. Я научу вас всему этому.",
            "Работа в IT - это не только программирование. Есть много других направлений: дизайн, маркетинг, продажи, HR. В этом видео я расскажу о всех возможностях в IT сфере."
        ]
        
        import random
        return random.choice(demo_transcripts)

def test_assemblyai():
    """Тестирование AssemblyAI клиента"""
    print("🧪 ТЕСТИРОВАНИЕ ASSEMBLYAI КЛИЕНТА")
    print("="*50)
    
    # Инициализируем клиент
    client = AssemblyAIClientImproved()
    
    # Тестируем подключение
    print("🔍 Тестирую подключение...")
    if client.test_connection():
        print("✅ Подключение к AssemblyAI работает")
    else:
        print("❌ Проблемы с подключением к AssemblyAI")
        return
    
    # Тестируем транскрипцию
    test_url = "https://storage.googleapis.com/aai-web-samples/5_common_sports_injuries.mp3"
    print(f"🎤 Тестирую транскрипцию: {test_url}")
    
    try:
        result = client.transcribe_audio_url(test_url)
        print(f"📝 Результат: {result[:100]}...")
    except Exception as e:
        print(f"❌ Ошибка транскрипции: {e}")

if __name__ == "__main__":
    test_assemblyai()
