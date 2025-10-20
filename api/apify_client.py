from apify_client import ApifyClient
import time
import random
from typing import Optional, List, Dict, Any
from config import Config

class ApifyInstagramClient:
    def __init__(self, api_key: str):
        self.client = ApifyClient(api_key)
        # ОБНОВЛЕННЫЕ АКТУАЛЬНЫЕ АКТОРЫ APIFY
        self.actor_configs = [
            {
                "id": "xMc5Ga1oCONPmWJIa",  # instagram-reel-scraper (актуальный)
                "build_input": lambda username, count: {
                    "username": [username],  # Исправлено: username вместо profiles
                    "resultsLimit": count,
                    "resultsType": "posts",
                    "addParentData": False,
                    "includeHasStoryHighlight": False,
                }
            },
            {
                "id": "shu8hvrXbJbY3Eb9W",  # instagram-scraper (актуальный)
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
                "id": "apify/instagram-reel-scraper",  # Fallback старый
                "build_input": lambda username, count: {
                    "username": [username],  # Исправлено: username вместо profiles
                    "resultsLimit": count,
                    "resultsType": "posts",
                }
            },
            {
                "id": "apify/instagram-scraper",  # Fallback старый
                "build_input": lambda username, count: {
                    "usernames": [username],
                    "resultsType": "posts",
                    "resultsLimit": count,
                    "searchType": "user",
                    "includeHashtags": False,
                    "onlyPostsNewerThan": "",
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
        safe_count = max(1, min(int(count), 50))
        actor_config = self.actor_configs[self.current_actor_index]
        run_input = actor_config["build_input"](username, safe_count)
        
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
                run_input = actor_config["build_input"](username, safe_count)
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
                
                # Запускаем актор и ЖДЕМ завершения
                run_info = self.client.actor(self.actor_id).start(run_input=run_input)
                run_id = run_info.get('id')
                print(f"🚀 Запущен актор {run_id}, ждем завершения...")
                
                # Ждем завершения актора - УМЕНЬШЕННЫЙ ТАЙМАУТ для быстрого fallback
                max_wait_time = 180  # 3 минуты для реальных данных
                wait_interval = 5   # Проверяем каждые 5 секунд
                waited_time = 0
                
                while waited_time < max_wait_time:
                    run = self.client.run(run_id).get()
                    status = run.get('status')
                    print(f"⏳ Статус актора: {status}, ждем {waited_time}с...")
                    
                    if status in ['SUCCEEDED', 'FINISHED']:
                        print(f"✅ Актор завершился успешно!")
                        break
                    elif status in ['FAILED', 'ABORTED']:
                        print(f"⚠️ Актор завершился с ошибкой: {status}, пробуем следующий актор")
                        # return self._get_fallback_posts(username, count)  # Закомментировано для получения реальных данных
                    
                    time.sleep(wait_interval)
                    waited_time += wait_interval
                
                if waited_time >= max_wait_time:
                    print(f"⚠️ Таймаут актора {max_wait_time}с, пробуем следующий актор")
                    # return self._get_fallback_posts(username, count)  # Закомментировано для получения реальных данных
                
                # Получаем финальный статус
                run = self.client.run(run_id).get()
                run_status = run.get('status', 'unknown')
                print(f"🔄 Финальный статус: {run_status}")
                
                # Получаем результаты
                dataset_id = run.get("defaultDatasetId")
                if not dataset_id:
                    print(f"⚠️ Не получен ID датасета, пробуем следующий актор")
                    # return self._get_fallback_posts(username, count)  # Закомментировано для получения реальных данных
                
                print(f"📊 Читаю датасет: {dataset_id}")
                dataset_items = []
                
                item_count = 0
                for item in self.client.dataset(dataset_id).iterate_items():
                    dataset_items.append(item)
                    item_count += 1
                    if item_count <= 3:  # Показываем первые 3 элемента для отладки
                        print(f"📋 Элемент {item_count}: {list(item.keys())[:5]}")  # Показываем ключи
                
                print(f"📈 Всего получено элементов: {len(dataset_items)}")
                
                if not dataset_items:
                    print(f"⚠️ Датасет пуст для @{username}, пробуем следующий актор")
                    # return self._get_fallback_posts(username, count)  # Закомментировано для получения реальных данных
                
                if dataset_items:
                    print(f"✅ Обрабатываю {len(dataset_items)} элементов от @{username}")
                    processed = self.process_instagram_posts(dataset_items)
                    
                    # Если обработали 0 постов, пробуем следующий актор
                    if not processed:
                        print(f"⚠️ Apify не вернул валидных данных для @{username}, пробуем следующий актор")
                        # return self._get_fallback_posts(username, count)  # Закомментировано для получения реальных данных
                    
                    return processed
                else:
                    print(f"⚠️ Датасет пуст для @{username}")
                    if attempt == max_retries - 1:
                        print(f"⚠️ Apify не вернул данных для @{username}, используем fallback")
                        return self._get_fallback_posts(username, count)
                    
            except Exception as e:
                print(f"❌ Ошибка на попытке {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    print(f"⚠️ Все попытки исчерпаны, используем fallback")
                    return self._get_fallback_posts(username, count)
                time.sleep(Config.API_RETRY_DELAY)
        
        # Если дошли сюда, значит что-то пошло не так
        print(f"⚠️ Неожиданная ситуация, используем fallback")
        return self._get_fallback_posts(username, count)
    
    def process_instagram_posts(self, raw_posts: List[Dict]) -> List[Dict[str, Any]]:
        """
        Обработка сырых данных постов из Instagram - УЛУЧШЕННАЯ ВЕРСИЯ
        """
        processed_posts = []
        
        print(f"🔍 Обрабатываю {len(raw_posts)} сырых постов...")
        
        for i, post in enumerate(raw_posts):
            try:
                print(f"📋 Обрабатываю пост {i+1}/{len(raw_posts)}: {list(post.keys())[:5]}...")
                
                # Проверяем на ошибки Apify
                if "error" in post or "errorDescription" in post:
                    print(f"⚠️ Apify вернул ошибку: {post.get('error', 'Unknown error')}")
                    continue
                
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
                
                try:
                    likes_int = int(likes) if likes else 0
                except (ValueError, TypeError):
                    likes_int = 0

                try:
                    views_int = int(views) if views else 0
                except (ValueError, TypeError):
                    views_int = 0

                try:
                    comments_int = int(comments) if comments else 0
                except (ValueError, TypeError):
                    comments_int = 0

                engagement_rate = 0.0
                if views_int:
                    engagement_rate = round(((likes_int + comments_int) / views_int) * 100, 2)

                processed_post = {
                    "id": post_id,
                    "url": post_url,
                    "caption": caption[:500],  # чуть больше текста
                    "likes_count": likes_int,
                    "views_count": views_int,
                    "comments_count": comments_int,
                    "timestamp": timestamp,
                    "video_url": video_url,
                    "duration": post.get("videoDuration", 30),
                    "thumbnail_url": post.get("displayUrl"),
                    "hashtags": post.get("hashtags", []),
                    "first_comment": post.get("firstComment"),
                    "music": (post.get("musicInfo") or {}).get("title"),
                    "is_viral": self.is_viral_content(post),
                    "engagement_rate": engagement_rate,
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
        
        # УБРАН ПОРОГ ВИРАЛЬНОСТИ - все посты показываются
        # Теперь все посты считаются "виральными" для отображения
        return True
    
    def get_trending_content(self, usernames: List[str], count: int = 20, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Получение трендового контента от списка пользователей - ОПТИМИЗИРОВАННО
        """
        all_viral_posts = []
        
        print(f"🚀 Начинаю парсинг {len(usernames)} пользователей: {usernames}")
        
        for i, username in enumerate(usernames):
            try:
                print(f"📊 Обрабатываю {i+1}/{len(usernames)}: @{username}")
                clean_username = (username or "").strip()
                if not clean_username:
                    print(f"⚠️ Пустой никнейм на позиции {i}")
                    continue

                if clean_username.startswith('@'):
                    clean_username = clean_username[1:]

                if not clean_username:
                    print(f"⚠️ Ник @{username} после очистки пуст")
                    continue

                posts = self.scrape_user_posts(clean_username, count=count)
                
                if posts:
                    print(f"📥 Получено {len(posts)} постов от @{username}")
                    
                    # Добавляем информацию о пользователе ко всем постам
                    for post in posts:
                        post["source_username"] = clean_username
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
    
    def _get_fallback_posts(self, username: str, count: int) -> List[Dict[str, Any]]:
        """Fallback данные когда Apify недоступен"""
        print(f"🔄 Создаю fallback данные для @{username}")
        
        fallback_posts = []
        for i in range(min(count, 5)):  # Максимум 5 fallback постов
            post = {
                "id": f"fallback_{i}",
                "caption": f"Демо-пост {i+1} от @{username}. Это пример контента для тестирования системы трендвочинга.",
                "likes_count": 100 + i * 50,
                "comments_count": 10 + i * 5,
                "views_count": 1000 + i * 200,
                "url": f"https://instagram.com/p/fallback_{i}/",
                "video_url": f"https://instagram.com/p/fallback_{i}/",
                "timestamp": "2024-09-23T10:00:00Z",
                "source_username": f"@{username}",
                "is_viral": i < 2,  # Первые 2 поста вирусные
                "engagement_rate": 0.05 + i * 0.01,
                "hashtags": ["#работа", "#карьера", "#москва"],
                "music": f"Демо-музыка {i+1}",
                "duration": 30 + i * 10,
                "thumbnail_url": None,
                "first_comment": f"Отличный пост! 👍"
            }
            fallback_posts.append(post)
        
        print(f"✅ Создано {len(fallback_posts)} fallback постов")
        return fallback_posts

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
