import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///content_factory.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Celery settings for background tasks
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Cloud storage settings
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
    GOOGLE_CLOUD_BUCKET = os.environ.get('GOOGLE_CLOUD_BUCKET')
    
    # API rate limiting
    API_RETRY_ATTEMPTS = 3
    API_RETRY_DELAY = 5  # seconds
    
    # Video settings
    VIDEO_FORMAT = 'mp4'
    VIDEO_ASPECT_RATIO = '9:16'  # Vertical
    AUDIO_DURATION_SECONDS = 40
    HEALTHCHECK_PATH = os.environ.get('HEALTHCHECK_PATH', '/health')

    # Значения API по умолчанию (можно переопределить через переменные окружения)
    DEFAULT_API_KEYS = {
        'openai_api_key': os.getenv('DEFAULT_OPENAI_API_KEY', ''),
        'elevenlabs_api_key': os.getenv('DEFAULT_ELEVENLABS_API_KEY', ''),
        'heygen_api_key': os.getenv('DEFAULT_HEYGEN_API_KEY', ''),
        'apify_api_key': os.getenv('DEFAULT_APIFY_API_KEY', ''),
        'assemblyai_api_key': os.getenv('DEFAULT_ASSEMBLYAI_API_KEY', '')
    }
