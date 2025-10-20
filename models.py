from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(50), nullable=False, unique=True)
    openai_assistant_id = db.Column(db.String(100))
    master_prompt = db.Column(db.Text)
    api_keys = db.Column(db.Text)  # JSON string with API keys
    additional_settings = db.Column(db.Text)  # JSON string for module-specific settings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_api_keys(self):
        if self.api_keys:
            return json.loads(self.api_keys)
        return {}
    
    def set_api_keys(self, keys_dict):
        self.api_keys = json.dumps(keys_dict)
    
    def get_additional_settings(self):
        if self.additional_settings:
            return json.loads(self.additional_settings)
        return {}
    
    def set_additional_settings(self, settings_dict):
        self.additional_settings = json.dumps(settings_dict)

class Competitors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    platform = db.Column(db.String(50), nullable=False, default='instagram')
    is_active = db.Column(db.Boolean, default=True)
    last_checked = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TaskStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(100), nullable=False, unique=True)
    module_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    current_step = db.Column(db.String(100))
    error_message = db.Column(db.Text)
    result_data = db.Column(db.Text)  # JSON string with results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_result_data(self):
        if self.result_data:
            return json.loads(self.result_data)
        return {}
    
    def set_result_data(self, data_dict):
        self.result_data = json.dumps(data_dict)

class VideoGeneration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(100), nullable=False)
    module_name = db.Column(db.String(50), nullable=False)
    source_text = db.Column(db.Text)
    generated_text = db.Column(db.Text)
    audio_file_url = db.Column(db.String(500))
    video_file_url = db.Column(db.String(500))
    heygen_video_id = db.Column(db.String(100))
    avatar_id = db.Column(db.String(100))
    voice_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExpertTopics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.Text, nullable=False)
    is_selected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Новые модели для модуля трендвотчинга
class TrendAnalysis(db.Model):
    """Основная таблица для анализа трендов"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='collecting')
    config = db.Column(db.Text)  # JSON с настройками
    results = db.Column(db.Text)  # JSON с результатами
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_config(self):
        if self.config:
            return json.loads(self.config)
        return {}
    
    def set_config(self, config_dict):
        self.config = json.dumps(config_dict)
    
    def get_results(self):
        if self.results:
            return json.loads(self.results)
        return {}
    
    def set_results(self, results_dict):
        self.results = json.dumps(results_dict)

class CompetitorData(db.Model):
    """Данные о конкурентах и их постах"""
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('trend_analysis.id'), nullable=False)
    competitor_handle = db.Column(db.String(100), nullable=False)
    post_url = db.Column(db.String(500), nullable=False)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    post_date = db.Column(db.DateTime)
    thumbnail_url = db.Column(db.String(500))
    is_selected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContentGeneration(db.Model):
    """Результаты генерации контента"""
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('trend_analysis.id'), nullable=False)
    selected_post_id = db.Column(db.Integer, db.ForeignKey('competitor_data.id'), nullable=True)
    original_transcript = db.Column(db.Text)
    rewritten_text = db.Column(db.Text)
    final_text = db.Column(db.Text)
    audio_file_url = db.Column(db.String(500))
    video_file_url = db.Column(db.String(500))
    generation_settings = db.Column(db.Text)  # JSON с настройками
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_generation_settings(self):
        if self.generation_settings:
            return json.loads(self.generation_settings)
        return {}
    
    def set_generation_settings(self, settings_dict):
        self.generation_settings = json.dumps(settings_dict)
