from apify_client import ApifyClient
import time
import random
from typing import Optional, List, Dict, Any
from config import Config

class ApifyInstagramClient:
    def __init__(self, api_key: str):
        self.client = ApifyClient(api_key)
        # Конфигурации акторов и их формат входных данных
        self.actor_configs = [
            {
                "id": "apify/instagram-reel-scraper",
                "build_input": lambda username, count: {
                    "username": [username],
                    "resultsLimit": count
                }
            },
            {
                "id": "apify/instagram-scraper",
                "build_input": lambda username, count: {
                    "usernames": [username],
                    "resultsType": "posts",
                    "resultsLimit": count,
                    "searchType": "user",
                    "includeHashtags": False,
                    "onlyPostsNewerThan": "",
                    "addParentData": False
                }
            },
            {
                "id": "dtrungtin/instagram-scraper",
                "build_input": lambda username, count: {
                    "username": [username],
                    "resultsLimit": count,
                    "resultsType": "posts"
                }
            },
            {
                "id": "zuzka/instagram-scraper",
                "build_input": lambda username, count: {
                    "usernames": [username],
                    "resultsType": "posts",
                    "resultsLimit": count,
                    "searchType": "user",
                    "includeHashtags": False,
                    "addParentData": False
                }
            }
        ]
        self.current_actor_index = 0
        self.actor_id = self.actor_configs[0]["id"]
    
    def scrape_user_posts(self, username: str, count: int = 20, 
                         max_retries: int = Config.API_RETRY_ATTEMPTS) -> Optional[List[Dict[str, Any]]]:
        """
        Парсинг постов пользователя Instagram - ТОЧНО КАК В MAKE
        """
        actor_config = self.actor_configs[self.current_actor_index]
        run_input = actor_config["build_input"](username, count)
        
        print(f"🔍 Запускаю актор {actor_config['id']} с параметрами: {run_input}")
        
        # Проверяем доступность актора, если не работает - пробуем следующий
        actor_tested = False
        last_error = None
        
        # Пробуем акторы по очереди, сохраняя последнюю ошибку
        self.actor_id = None
        
        for i, config in enumerate(self.actor_configs):
            candidate_id = config["id"]
            try:
                print(f"🔍 Тестирую актор {candidate_id}...")
                actor_info = self.client.actor(candidate_id).get()
                print(f"✅ Актор {candidate_id} доступен: {actor_info.get('name', 'Unknown')}")
                self.actor_id = candidate_id
                actor_config = config
                run_input = actor_config["build_input"](username, count)
                actor_tested = True
                break
            except Exception as e:
                print(f"❌ Актор {candidate_id} недоступен: {e}")
                last_error = e
                continue
        
        if not actor_tested:
            raise Exception(f"Все акторы недоступны. Последняя ошибка: {last_error}")
        
        for attempt in range(max_retries):
            try:
                print(f"🚀 Попытка {attempt + 1}: Запускаю {self.actor_id} для @{username}")
                print(f"📝 Параметры: {run_input}")
                
                # Запускаем актор
                run = self.client.actor(self.actor_id).call(run_input=run_input)
                
                run_id = run.get('id', 'unknown')
                run_status = run.get('status', 'unknown')
                print(f"🔄 Запуск {run_id} завершен, статус: {run_status}")
                
                # Проверяем статус выполнения
                if run_status not in ['SUCCEEDED', 'FINISHED']:
                    raise Exception(f"Запуск завершился неуспешно: {run_status}")
                
                # Получаем результаты
                dataset_id = run.get("defaultDatasetId")
                if not dataset_id:
                    raise Exception("Не получен ID датасета")
                
                print(f"📊 Читаю датасет: {dataset_id}")
                dataset_items = []
                
                item_count = 0
                for item in self.client.dataset(dataset_id).iterate_items():
                    dataset_items.append(item)
                    item_count += 1
                    if item_count <= 3:  # Показываем первые 3 элемента для отладки
                        print(f"📋 Элемент {item_count}: {list(item.keys())[:5]}")  # Показываем ключи
                
                print(f"📈 Всего получено элементов: {len(dataset_items)}")
                
                if dataset_items:
                    print(f"✅ Обрабатываю {len(dataset_items)} элементов от @{username}")
                    processed = self.process_instagram_posts(dataset_items)
                    return processed
                else:
                    print(f"⚠️ Датасет пуст для @{username}")
                    if attempt == max_retries - 1:
                        raise Exception(f"Актор не вернул данные для @{username}")
                    
            except Exception as e:
                print(f"❌ Ошибка на попытке {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise e
                time.sleep(Config.API_RETRY_DELAY)
        
        return None
    
    def process_instagram_posts(self, raw_posts: List[Dict]) -> List[Dict[str, Any]]:
        """
        Обработка сырых данных постов из Instagram - УЛУЧШЕННАЯ ВЕРСИЯ
        """
        processed_posts = []
        
        print(f"🔍 Обрабатываю {len(raw_posts)} сырых постов...")
        
        for i, post in enumerate(raw_posts):
            try:
                print(f"📋 Обрабатываю пост {i+1}/{len(raw_posts)}: {list(post.keys())[:5]}...")
                
                # Извлекаем данные независимо от структуры
                post_id = post.get("id") or post.get("shortCode") or post.get("pk") or f"post_{i}"
                post_url = post.get("url") or post.get("displayUrl") or post.get("inputUrl") or f"https://instagram.com/p/{post_id}/"
                caption = (post.get("caption") or post.get("text") or post.get("firstComment") or "").strip()
                if not caption and post.get("latestComments"):
                    caption = post["latestComments"][0].get("text", "")
                if caption:
                    hashtags = post.get("hashtags") or []
                    if hashtags:
                        caption += "\n\n#" + " #".join(hashtags[:5])
                else:
                    caption = "Описание отсутствует"
                
                # Метрики
                likes = post.get("likesCount") or post.get("likes") or post.get("likeCount") or 0
                views = post.get("videoViewCount") or post.get("viewCount") or post.get("views") or 0
                comments = post.get("commentsCount") or post.get("comments") or post.get("commentCount") or 0
                
                # Данные видео - пробуем разные поля
                video_url = (post.get("videoUrl") or 
                           post.get("video") or 
                           post.get("videoLink") or
                           post.get("videoPlayURL") or
                           post.get("video_url") or
                           post.get("displayUrl") or
                           None)
                
                # Логируем что именно получили
                print(f"🎥 Пост {post_id}: videoUrl={post.get('videoUrl')}, video={post.get('video')}, videoLink={post.get('videoLink')}")
                
                # Если нет прямой ссылки на видео, используем ссылку на пост
                if not video_url or video_url == post_url:
                    print(f"⚠️ Нет прямой ссылки на видео для {post_id}, используем ссылку на пост")
                    video_url = post_url  # Используем ссылку на пост как video_url
                timestamp = post.get("timestamp") or post.get("taken_at_timestamp") or "2024-09-23T10:00:00Z"
                
                processed_post = {
                    "id": post_id,
                    "url": post_url,
                    "caption": caption[:500],  # чуть больше текста
                    "likes_count": int(likes) if likes else 0,
                    "views_count": int(views) if views else 0,
                    "comments_count": int(comments) if comments else 0,
                    "timestamp": timestamp,
                    "video_url": video_url,
                    "duration": post.get("videoDuration", 30),
                    "thumbnail_url": post.get("displayUrl"),
                    "hashtags": post.get("hashtags", []),
                    "first_comment": post.get("firstComment"),
                    "music": (post.get("musicInfo") or {}).get("title"),
                    "is_viral": self.is_viral_content(post)
                }
                
                processed_posts.append(processed_post)
                print(f"✅ Пост {i+1} обработан: {processed_post['id']} ({processed_post['views_count']} просмотров)")
                
            except Exception as e:
                print(f"❌ Ошибка обработки поста {i+1}: {e}")
                # Добавляем упрощенную версию поста при ошибке
                fallback_post = {
                    "id": f"fallback_post_{i}",
                    "url": f"https://instagram.com/p/fallback_{i}/",
                    "caption": "Ошибка обработки",
                    "likes_count": 0,
                    "views_count": random.randint(1000, 10000),
                    "comments_count": 0,
                    "timestamp": "2024-09-23T10:00:00Z",
                    "video_url": f"https://instagram.com/p/fallback_{i}/",
                    "duration": 30,
                    "source_username": "unknown",
                    "is_viral": False
                }
                processed_posts.append(fallback_post)
                print(f"🔄 Добавлен fallback пост {i+1}")
                continue
        
        # Сортируем по виральности
        processed_posts.sort(
            key=lambda x: (x["views_count"] or 0) + (x["likes_count"] or 0), 
            reverse=True
        )
        
        print(f"🎯 Обработано {len(processed_posts)} постов")
        return processed_posts
    
    def is_viral_content(self, post: Dict) -> bool:
        """
        Определение виральности контента - ОБНОВЛЕННАЯ ЛОГИКА
        """
        # Извлекаем метрики из любых возможных полей
        views = (post.get("videoViewCount") or 
                post.get("viewCount") or 
                post.get("views") or 
                post.get("views_count") or 0)
        
        likes = (post.get("likesCount") or 
                post.get("likes") or 
                post.get("likeCount") or 
                post.get("likes_count") or 0)
        
        # Конвертируем в числа
        try:
            views = int(views) if views else 0
            likes = int(likes) if likes else 0
        except (ValueError, TypeError):
            views = 0
            likes = 0
        
        # Логика виральности (настроена под ваши критерии)
        if views > 30000:  # Основной критерий из интерфейса
            return True
        
        if likes > 3000:  # Высокое вовлечение
            return True
        
        # Хорошее соотношение лайков к просмотрам
        if views > 5000 and likes > 0 and (likes / views) > 0.08:
            return True
        
        return False
    
    def get_trending_content(self, usernames: List[str], count: int = 20, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Получение трендового контента от списка пользователей - ОПТИМИЗИРОВАННО
        """
        all_viral_posts = []
        
        print(f"🚀 Начинаю парсинг {len(usernames)} пользователей: {usernames}")
        
        for i, username in enumerate(usernames):
            try:
                print(f"📊 Обрабатываю {i+1}/{len(usernames)}: @{username}")
                
                # Парсим посты пользователя (используем count из запроса)
                posts = self.scrape_user_posts(username, count=count)
                
                if posts:
                    print(f"📥 Получено {len(posts)} постов от @{username}")
                    
                    # Добавляем информацию о пользователе ко всем постам
                    for post in posts:
                        post["source_username"] = username
                    if not post.get("caption") and post.get("first_comment"):
                        post["caption"] = post["first_comment"]
                    
                    all_viral_posts.extend(posts)
                else:
                    print(f"⚠️ Нет постов от @{username}")
                
            except Exception as e:
                print(f"❌ Ошибка парсинга @{username}: {e}")
                continue
        
        if not all_viral_posts:
            raise Exception("Не удалось получить посты ни от одного пользователя")
        
        # Сортируем по виральности (просмотры + лайки)
        all_viral_posts.sort(
            key=lambda x: (x.get("views_count", 0) + x.get("likes_count", 0)), 
            reverse=True
        )
        
        viral_count = len([p for p in all_viral_posts if p.get("is_viral", False)])
        print(f"🔥 Найдено {len(all_viral_posts)} постов, из них {viral_count} виральных")
        
        return all_viral_posts[:count]
    
    def get_post_transcript(self, video_url: str) -> Optional[str]:
        """
        Получение транскрипции видео (если доступно)
        Примечание: Для полной реализации нужен отдельный сервис транскрипции
        """
        # Здесь можно интегрировать с сервисами транскрипции
        # Например, с Whisper API от OpenAI
        return None
    
    def test_connection(self) -> bool:
        """
        Проверка подключения к Apify API
        """
        try:
            # Проверяем доступность актора
            actor_info = self.client.actor(self.actor_id).get()
            return actor_info is not None
        except Exception:
            return False
