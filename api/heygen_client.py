import os
import requests
import time
from typing import Optional, List, Dict, Any
import urllib3

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HeyGenClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key if api_key else os.getenv("HEYGEN_API_KEY", "")
        self.base_url = "https://api.heygen.com/v2"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        if self.api_key:
            self.headers["x-api-key"] = self.api_key
    
    def get_available_avatars(self) -> List[Dict[str, Any]]:
        """
        Получение списка доступных аватаров (обновлено для v2 API)
        """
        if not self.api_key:
            print("HeyGen API key not configured")
            return self._get_fallback_avatars()

        try:
            response = requests.get(
                f"{self.base_url}/avatars", 
                headers=self.headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            avatars_data = response.json()
            if avatars_data.get("error"):
                print(f"HeyGen API error: {avatars_data.get('error')}")
                return self._get_fallback_avatars()
            
            avatars = avatars_data.get("data", {}).get("avatars", [])
            return [
                {
                    "avatar_id": avatar["avatar_id"],
                    "avatar_name": avatar["avatar_name"],
                    "preview_image_url": avatar.get("preview_image_url", ""),
                    "preview_video_url": avatar.get("preview_video_url", ""),
                    "gender": avatar.get("gender", ""),
                    "avatar_type": avatar.get("avatar_type", "")
                }
                for avatar in avatars
            ]
        except Exception as e:
            print(f"Error getting avatars: {e}")
            return self._get_fallback_avatars()
    
    def _get_fallback_avatars(self) -> List[Dict[str, Any]]:
        """Fallback аватары если API недоступен"""
        return [
            {
                "avatar_id": "demo_avatar_1",
                "avatar_name": "Demo Avatar 1",
                "preview_image_url": "https://via.placeholder.com/200x200/007bff/ffffff?text=Avatar+1",
                "preview_video_url": "",
                "gender": "male",
                "avatar_type": "demo"
            },
            {
                "avatar_id": "demo_avatar_2", 
                "avatar_name": "Demo Avatar 2",
                "preview_image_url": "https://via.placeholder.com/200x200/28a745/ffffff?text=Avatar+2",
                "preview_video_url": "",
                "gender": "female",
                "avatar_type": "demo"
            }
        ]
    
    def create_video(self, avatar_id: str = "default_avatar", audio_url: str = "", 
                    video_format: str = "vertical", max_retries: int = 3) -> Optional[str]:
        """
        Создание видео с говорящей головой (обновлено для v2 API с audio_url)
        """
        if not self.api_key:
            print("HeyGen API key not configured")
            return self._create_video_placeholder()

        if not audio_url:
            print("Audio URL is required for video generation")
            return self._create_video_placeholder()

        url = f"{self.base_url}/video/generate"
        
        # Определяем размеры в зависимости от формата
        if video_format == "vertical":
            width, height = 720, 1280  # 9:16 для вертикального видео
        elif video_format == "horizontal":
            width, height = 1280, 720  # 16:9 для горизонтального видео
        else:  # square
            width, height = 720, 720   # 1:1 для квадратного видео
        
        # Обновленный payload согласно документации HeyGen v2
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "audio",
                        "audio_url": audio_url
                    }
                }
            ],
            "dimension": {
                "width": width,
                "height": height
            }
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=self.headers, verify=False, timeout=60)
                
                print(f"HeyGen API response status: {response.status_code}")
                print(f"HeyGen API response: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"HeyGen API success: {result}")
                    
                    # Проверяем структуру ответа
                    if "data" in result and "video_id" in result["data"]:
                        video_id = result["data"]["video_id"]
                        print(f"✅ Получен video_id: {video_id}")
                        return video_id
                    elif "video_id" in result:
                        video_id = result["video_id"]
                        print(f"✅ Получен video_id (прямой): {video_id}")
                        return video_id
                    else:
                        print(f"❌ Не найден video_id в ответе: {result}")
                        return None
                else:
                    print(f"HeyGen API error {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"HeyGen attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print("❌ Все попытки исчерпаны, возвращаем None")
                    return None
                time.sleep(2)
        
        print("❌ Все попытки исчерпаны, возвращаем None")
        return None
    
    def _create_video_placeholder(self) -> str:
        """Создает заглушку видео для демонстрации"""
        # Возвращаем публично доступное демо видео
        return "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    
    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Проверка статуса генерации видео (обновлено для v1 API)
        """
        try:
            # Используем правильный endpoint согласно документации
            response = requests.get(
                f"https://api.heygen.com/v1/video_status.get?video_id={video_id}", 
                headers=self.headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 100:
                data = result.get("data", {})
                return {
                    "status": data.get("status"),
                    "video_url": data.get("video_url"),
                    "duration": data.get("duration"),
                    "thumbnail_url": data.get("thumbnail_url"),
                    "gif_url": data.get("gif_url"),
                    "caption_url": data.get("caption_url"),
                    "error": data.get("error")
                }
            else:
                return {"status": "error", "error_message": str(result)}
                
        except Exception as e:
            return {"status": "error", "error_message": str(e)}
    
    def get_latest_video(self) -> Optional[str]:
        """
        Получить URL последнего сгенерированного видео через HeyGen API
        """
        if not self.api_key:
            print("HeyGen API key not configured")
            return None
            
        try:
            # Используем endpoint для получения списка видео
            response = requests.get(
                f"{self.base_url}/video.list",
                headers=self.headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 100:
                data = result.get("data", {})
                videos = data.get("videos", [])
                if videos:
                    # Берем первое видео (самое свежее)
                    latest_video = videos[0]
                    return latest_video.get("video_url")
            return None
            
        except Exception as e:
            print(f"Error getting latest video: {e}")
            return None
    
    def wait_for_video_completion(self, video_id: str, timeout: int = 600) -> Optional[str]:
        """
        Ожидание завершения генерации видео и получение URL
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_data = self.get_video_status(video_id)
            status = status_data.get("status")
            
            if status == "completed":
                return status_data.get("video_url")
            elif status == "failed":
                raise Exception(f"Video generation failed: {status_data.get('error_message')}")
            
            time.sleep(10)  # Проверяем каждые 10 секунд
        
        raise Exception("Video generation timeout")
    
    def save_video_to_cloud(self, video_url: str, filename: str) -> str:
        """
        Скачивание видео и сохранение в облачное хранилище
        """
        from api.cloud_storage import CloudStorageClient
        
        # Скачиваем видео
        response = requests.get(video_url)
        response.raise_for_status()
        
        cloud_client = CloudStorageClient()
        
        # Создаем путь с датой
        from datetime import datetime
        date_path = datetime.now().strftime("%Y/%m/%d")
        full_path = f"videos/{date_path}/{filename}"
        
        return cloud_client.upload_file(response.content, full_path, content_type="video/mp4")
    
    def generate_video(self, audio_url: str, avatar_id: str = "default_avatar") -> Optional[str]:
        """
        Простая генерация видео с fallback
        """
        if not self.api_key:
            print("HeyGen API key not configured")
            return self._create_video_placeholder()

        try:
            # Сначала пробуем реальный API
            video_id = self.create_video(avatar_id, audio_url)
            
            if video_id and video_id != "demo_video_id":
                # Если получили реальный video_id, возвращаем его
                return video_id
            
        except Exception as e:
            print(f"HeyGen API недоступен: {e}")
        
        # Fallback: возвращаем заглушку видео
        return self._create_video_placeholder()

    def generate_video_complete(self, avatar_id: str, audio_url: str, video_format: str = "vertical") -> Optional[str]:
        """
        Полный пайплайн: создание видео -> ожидание -> сохранение в облако
        """
        if not self.api_key:
            print("HeyGen API key not configured")
            return None

        try:
            # Создаем видео
            video_id = self.create_video(avatar_id, audio_url, video_format)
            if not video_id:
                return None
            
            # Ждем завершения
            video_url = self.wait_for_video_completion(video_id)
            if not video_url:
                return None
            
            # Сохраняем в облако
            filename = f"video_{video_id}.mp4"
            cloud_url = self.save_video_to_cloud(video_url, filename)
            
            return cloud_url
            
        except Exception as e:
            print(f"Error in video generation pipeline: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Проверка подключения к HeyGen API
        """
        if not self.api_key:
            return False
        try:
            response = requests.get(f"{self.base_url}/avatars", headers=self.headers)
            return response.status_code == 200
        except Exception:
            return False
