import requests
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
import time

class ApifyTrendsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.apify.com/v2"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def parse_instagram_posts(self, usernames: List[str], days_back: int = 7) -> List[Dict]:
        """Парсинг постов Instagram конкурентов"""
        try:
            # Настройки для Instagram Scraper
            input_data = {
                "usernames": usernames,
                "resultsType": "posts",
                "resultsLimit": 50,
                "addParentData": False,
                "addUserInfo": True,
                "addHighlights": False,
                "addStories": False,
                "addTagged": False,
                "addLocationInfo": True,
                "addPreview": True,
                "addPreviewText": True,
                "addSidecar": True,
                "addVideoPreview": True,
                "addVideoPreviewText": True,
                "addVideoPreviewDuration": True,
                "addVideoPreviewAspectRatio": True,
                "addVideoPreviewPlayCount": True,
                "addVideoPreviewViews": True,
                "addVideoPreviewLikes": True,
                "addVideoPreviewComments": True,
                "addVideoPreviewTimestamp": True,
                "addVideoPreviewUrl": True,
                "addVideoPreviewThumbnail": True,
                "addVideoPreviewCaption": True,
                "addVideoPreviewHashtags": True,
                "addVideoPreviewMentions": True,
                "addVideoPreviewLocation": True,
                "addVideoPreviewUser": True
            }
            
            # Запускаем актер
            actor_id = "apify/instagram-scraper"
            run_response = self._run_actor(actor_id, input_data)
            
            if not run_response.get('success'):
                raise Exception(f"Failed to start actor: {run_response.get('error')}")
            
            run_id = run_response['data']['id']
            
            # Ждем завершения
            result = self._wait_for_completion(run_id)
            
            # Обрабатываем результаты
            processed_posts = self._process_posts(result, days_back)
            
            return processed_posts
            
        except Exception as e:
            print(f"Error parsing Instagram posts: {str(e)}")
            return []
    
    def _run_actor(self, actor_id: str, input_data: Dict) -> Dict:
        """Запуск актера Apify"""
        try:
            url = f"{self.base_url}/acts/{actor_id}/runs"
            response = requests.post(url, headers=self.headers, json=input_data)
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'data': response.json()['data']
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _wait_for_completion(self, run_id: str, max_wait_time: int = 300) -> List[Dict]:
        """Ожидание завершения выполнения"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Проверяем статус
                status_url = f"{self.base_url}/actor-runs/{run_id}"
                response = requests.get(status_url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()['data']
                    status = data['status']
                    
                    if status == 'SUCCEEDED':
                        # Получаем результаты
                        results_url = f"{self.base_url}/actor-runs/{run_id}/dataset/items"
                        results_response = requests.get(results_url, headers=self.headers)
                        
                        if results_response.status_code == 200:
                            return results_response.json()
                    
                    elif status == 'FAILED':
                        raise Exception("Actor run failed")
                    
                    elif status in ['READY', 'RUNNING']:
                        time.sleep(10)  # Ждем 10 секунд
                        continue
                
            except Exception as e:
                print(f"Error checking status: {str(e)}")
                time.sleep(10)
        
        raise Exception("Timeout waiting for completion")
    
    def _process_posts(self, posts: List[Dict], days_back: int) -> List[Dict]:
        """Обработка и фильтрация постов"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            processed = []
            
            for post in posts:
                # Фильтруем по дате
                post_date = self._parse_date(post.get('timestamp'))
                if post_date and post_date < cutoff_date:
                    continue
                
                # Обрабатываем метрики
                views = self._extract_views(post)
                likes = post.get('likesCount', 0)
                comments = post.get('commentsCount', 0)
                
                # Вычисляем engagement rate
                engagement_rate = self._calculate_engagement_rate(views, likes, comments)
                
                processed_post = {
                    'username': post.get('ownerUsername', ''),
                    'url': post.get('url', ''),
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'engagement_rate': engagement_rate,
                    'timestamp': post.get('timestamp'),
                    'thumbnail_url': post.get('displayUrl', ''),
                    'caption': post.get('caption', ''),
                    'is_video': post.get('isVideo', False),
                    'video_url': post.get('videoUrl', ''),
                    'hashtags': self._extract_hashtags(post.get('caption', '')),
                    'mentions': self._extract_mentions(post.get('caption', ''))
                }
                
                processed.append(processed_post)
            
            # Сортируем по engagement rate
            processed.sort(key=lambda x: x['engagement_rate'], reverse=True)
            
            return processed
            
        except Exception as e:
            print(f"Error processing posts: {str(e)}")
            return []
    
    def _parse_date(self, date_str: str) -> datetime:
        """Парсинг даты из строки"""
        try:
            if not date_str:
                return None
            
            # Пробуем разные форматы
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _extract_views(self, post: Dict) -> int:
        """Извлечение количества просмотров"""
        try:
            # Для видео
            if post.get('isVideo'):
                return post.get('videoViewCount', 0)
            
            # Для обычных постов - используем лайки как приблизительный показатель
            return post.get('likesCount', 0)
            
        except Exception:
            return 0
    
    def _calculate_engagement_rate(self, views: int, likes: int, comments: int) -> float:
        """Вычисление engagement rate"""
        try:
            if views == 0:
                return 0.0
            
            total_engagement = likes + comments
            return round((total_engagement / views) * 100, 2)
            
        except Exception:
            return 0.0
    
    def _extract_hashtags(self, caption: str) -> List[str]:
        """Извлечение хештегов из подписи"""
        try:
            import re
            hashtags = re.findall(r'#\w+', caption)
            return [tag.lower() for tag in hashtags]
        except Exception:
            return []
    
    def _extract_mentions(self, caption: str) -> List[str]:
        """Извлечение упоминаний из подписи"""
        try:
            import re
            mentions = re.findall(r'@\w+', caption)
            return [mention.lower() for mention in mentions]
        except Exception:
            return []
    
    def get_actor_status(self, run_id: str) -> Dict:
        """Получение статуса выполнения актера"""
        try:
            url = f"{self.base_url}/actor-runs/{run_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()['data']
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
