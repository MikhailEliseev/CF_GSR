from google.cloud import storage
import io
from typing import Optional
from config import Config
import os

class CloudStorageClient:
    def __init__(self):
        # Инициализация клиента Google Cloud Storage
        # Предполагается, что файл аутентификации находится в переменной окружения
        # GOOGLE_APPLICATION_CREDENTIALS
        self.client = storage.Client(project=Config.GOOGLE_CLOUD_PROJECT)
        self.bucket_name = Config.GOOGLE_CLOUD_BUCKET
        self.bucket = self.client.bucket(self.bucket_name)
    
    def upload_file(self, file_data: bytes, file_path: str, content_type: str) -> str:
        """
        Загрузка файла в облачное хранилище
        
        Args:
            file_data: Данные файла в байтах
            file_path: Путь файла в bucket (например, "audio/2024/01/15/speech_123.mp3")
            content_type: MIME тип файла
        
        Returns:
            Публичный URL загруженного файла
        """
        try:
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(file_data, content_type=content_type)
            
            # Делаем файл публично доступным
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            print(f"Error uploading file to cloud storage: {e}")
            raise e
    
    def upload_file_from_path(self, local_file_path: str, cloud_file_path: str) -> str:
        """
        Загрузка файла из локального пути
        """
        try:
            blob = self.bucket.blob(cloud_file_path)
            blob.upload_from_filename(local_file_path)
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            print(f"Error uploading file from path: {e}")
            raise e
    
    def download_file(self, cloud_file_path: str, local_file_path: str) -> bool:
        """
        Скачивание файла из облака
        """
        try:
            blob = self.bucket.blob(cloud_file_path)
            blob.download_to_filename(local_file_path)
            return True
            
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
    
    def delete_file(self, cloud_file_path: str) -> bool:
        """
        Удаление файла из облака
        """
        try:
            blob = self.bucket.blob(cloud_file_path)
            blob.delete()
            return True
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """
        Список файлов в bucket с заданным префиксом
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def get_file_url(self, cloud_file_path: str) -> Optional[str]:
        """
        Получение публичного URL файла
        """
        try:
            blob = self.bucket.blob(cloud_file_path)
            if blob.exists():
                return blob.public_url
            return None
            
        except Exception as e:
            print(f"Error getting file URL: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Проверка подключения к облачному хранилищу
        """
        try:
            # Пытаемся получить информацию о bucket
            bucket_info = self.bucket.reload()
            return True
        except Exception:
            return False


class LocalStorageClient:
    """
    Локальный клиент для хранения файлов (fallback если облако недоступно)
    """
    def __init__(self):
        self.upload_dir = Config.UPLOAD_FOLDER
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def upload_file(self, file_data: bytes, file_path: str, content_type: str) -> str:
        """
        Сохранение файла локально
        """
        full_path = os.path.join(self.upload_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(file_data)
        
        # Возвращаем относительный URL
        return f"/uploads/{file_path}"
    
    def upload_file_from_path(self, local_file_path: str, cloud_file_path: str) -> str:
        """
        Копирование файла в upload директорию
        """
        import shutil
        
        full_path = os.path.join(self.upload_dir, cloud_file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        shutil.copy2(local_file_path, full_path)
        
        return f"/uploads/{cloud_file_path}"
