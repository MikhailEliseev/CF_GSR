from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models import db, Settings, TaskStatus, VideoGeneration
from api.openai_client import OpenAIClient

from api.elevenlabs_simple import ElevenLabsSimple
from api.heygen_client import HeyGenClient
from api.cloud_storage import CloudStorageClient, LocalStorageClient
from flask_socketio import SocketIO
import time

class BaseModule(ABC):
    """
    Базовый класс для всех модулей контент-завода
    """
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.settings = Settings.query.filter_by(module_name=module_name).first()
        
        if not self.settings:
            raise Exception(f"Settings for module {module_name} not found")
        
        # Инициализация API клиентов
        self._init_api_clients()
    
    def _init_api_clients(self):
        """
        Инициализация API клиентов на основе настроек
        """
        api_keys = self.settings.get_api_keys()
        
        # OpenAI клиент
        openai_key = api_keys.get('openai_api_key')
        if openai_key:
            self.openai_client = OpenAIClient(openai_key)
        else:
            self.openai_client = None
        
        # ElevenLabs клиент
        elevenlabs_key = api_keys.get('elevenlabs_api_key')
        if elevenlabs_key:
            self.elevenlabs_client = ElevenLabsSimple(elevenlabs_key)
        else:
            self.elevenlabs_client = None
        
        # HeyGen клиент
        heygen_key = api_keys.get('heygen_api_key')
        if heygen_key:
            self.heygen_client = HeyGenClient(heygen_key)
        else:
            self.heygen_client = None
        
        # Cloud Storage клиент
        try:
            self.storage_client = CloudStorageClient()
        except Exception:
            # Fallback на локальное хранилище
            self.storage_client = LocalStorageClient()
    
    def update_task_progress(self, task_id: str, progress: int, step: str, 
                           error_message: str = None, result_data: Dict = None):
        """
        Обновление прогресса задачи
        """
        task = TaskStatus.query.filter_by(task_id=task_id).first()
        if task:
            task.progress = progress
            task.current_step = step
            
            if error_message:
                task.status = 'failed'
                task.error_message = error_message
            elif progress >= 100:
                task.status = 'completed'
            else:
                task.status = 'processing'
            
            if result_data:
                task.set_result_data(result_data)
            
            db.session.commit()
            
            # Отправляем обновление через WebSocket
            self._emit_progress_update(task_id, {
                'progress': progress,
                'step': step,
                'status': task.status,
                'error_message': error_message,
                'result_data': result_data
            })
    
    def _emit_progress_update(self, task_id: str, data: Dict):
        """
        Отправка обновления прогресса через WebSocket
        """
        try:
            from app import socketio
            socketio.emit('task_update', data, room=task_id)
        except Exception:
            # WebSocket может быть недоступен в фоновых задачах
            pass
    
    def generate_text_content(self, context: str) -> Optional[str]:
        """
        Генерация текста с помощью OpenAI Assistant
        """
        if not self.openai_client or not self.settings.openai_assistant_id:
            raise Exception("OpenAI client or assistant ID not configured")
        
        redpolicy_path = self.settings.redpolicy_pdf_path
        return self.openai_client.generate_text_for_video(
            self.settings.openai_assistant_id,
            self.settings.master_prompt,
            context,
            redpolicy_path=redpolicy_path
        )
    
    def generate_speech(self, text: str, voice_id: str) -> Optional[str]:
        """
        Генерация речи с помощью ElevenLabs
        """
        if not self.elevenlabs_client:
            raise Exception("ElevenLabs client not configured")
        
        return self.elevenlabs_client.generate_speech_for_video(text, voice_id)
    
    def generate_video(self, audio_url: str, avatar_id: str) -> Optional[str]:
        """
        Генерация видео с помощью HeyGen
        """
        if not self.heygen_client:
            raise Exception("HeyGen client not configured")
        
        return self.heygen_client.generate_video_complete(avatar_id, audio_url)
    
    def save_generation_result(self, task_id: str, text: str, audio_url: str, 
                             video_url: str, avatar_id: str, voice_id: str):
        """
        Сохранение результата генерации в базу данных
        """
        generation = VideoGeneration(
            task_id=task_id,
            module_name=self.module_name,
            generated_text=text,
            audio_file_url=audio_url,
            video_file_url=video_url,
            avatar_id=avatar_id,
            voice_id=voice_id
        )
        db.session.add(generation)
        db.session.commit()
    
    def execute_full_pipeline(self, task_id: str, context: str, voice_id: str, avatar_id: str):
        """
        Выполнение полного пайплайна генерации видео
        """
        try:
            # Шаг 1: Генерация текста
            self.update_task_progress(task_id, 10, "Генерация текста...")
            text = self.generate_text_content(context)
            if not text:
                raise Exception("Failed to generate text")
            
            # Шаг 2: Генерация речи
            self.update_task_progress(task_id, 40, "Генерация речи...")
            audio_url = self.generate_speech(text, voice_id)
            if not audio_url:
                raise Exception("Failed to generate speech")
            
            # Шаг 3: Генерация видео
            self.update_task_progress(task_id, 70, "Генерация видео...")
            video_url = self.generate_video(audio_url, avatar_id)
            if not video_url:
                raise Exception("Failed to generate video")
            
            # Шаг 4: Сохранение результата
            self.update_task_progress(task_id, 90, "Сохранение результата...")
            self.save_generation_result(task_id, text, audio_url, video_url, avatar_id, voice_id)
            
            # Завершение
            result_data = {
                'text': text,
                'audio_url': audio_url,
                'video_url': video_url,
                'avatar_id': avatar_id,
                'voice_id': voice_id
            }
            self.update_task_progress(task_id, 100, "Готово!", result_data=result_data)
            
            return result_data
            
        except Exception as e:
            self.update_task_progress(task_id, 0, "Ошибка", error_message=str(e))
            raise e
    
    @abstractmethod
    def prepare_context(self, **kwargs) -> str:
        """
        Подготовка контекста для генерации текста (реализуется в каждом модуле)
        """
        pass
    
    @abstractmethod
    def start_generation(self, task_id: str, **kwargs):
        """
        Запуск процесса генерации (реализуется в каждом модуле)
        """
        pass
