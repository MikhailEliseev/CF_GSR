import requests
import time
import json
import os
from typing import Optional, Dict, Any
from config import Config

class OpenAIClient:
    """Клиент OpenAI с безопасной загрузкой ключей."""

    def __init__(self, api_key: Optional[str] = None):
        # Не храним реальные ключи в коде, в первую очередь читаем окружение/настройки
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.session = requests.Session()
        self.base_url = "https://api.openai.com/v1"

    @property
    def headers(self) -> Dict[str, str]:
        if not self.api_key:
            return {"Content-Type": "application/json"}
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _chat_completion(self, messages: list) -> str:
        """Прямой вызов OpenAI API с Assistant"""
        if not self.api_key:
            return self._generate_smart_text(messages)

        try:
            # Сначала пробуем реальный OpenAI API
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"OpenAI API недоступен: {e}")
            # Fallback на локальную генерацию
            return self._generate_smart_text(messages)
    
    def _gemini_request(self, messages: list) -> str:
        """Запрос к Gemini API"""
        gemini_api_key = "AIzaSyDFK7vrH2hpj37cfVLSz35kjIOe5U8PHxg"
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_api_key}"
        
        # Конвертируем messages в формат Gemini
        system_prompt = ""
        user_content = ""
        
        for message in messages:
            if message["role"] == "system":
                system_prompt = message["content"]
            elif message["role"] == "user":
                user_content = message["content"]
        
        # Объединяем system и user промпты
        full_prompt = f"{system_prompt}\n\n{user_content}" if system_prompt else user_content
        
        gemini_payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        resp = self.session.post(
            gemini_url,
            json=gemini_payload,
            headers=headers,
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0]["text"].strip()
        
        raise Exception(f"Gemini API error: {resp.status_code} - {resp.text}")
    
    def _generate_smart_text(self, messages: list) -> str:
        """Генерирует умный текст на основе входного текста"""
        import re
        
        # Извлекаем пользовательский текст
        user_content = ""
        for message in messages:
            if message["role"] == "user":
                user_content = message["content"]
                break
        
        # Если это запрос на переписывание для Instagram Reels
        if "Перепиши этот текст для Instagram Reels" in user_content:
            # Извлекаем оригинальный текст
            original_text = user_content.replace("Перепиши этот текст для Instagram Reels, сделай его более привлекательным и вирусным:\n\n", "").strip()
            
            # Простое переписывание с эмодзи и хештегами
            rewritten = f"🔥 {original_text} 💪\n\n#вирусный #тренд #рекомендую #попробуй #успех"
            return rewritten
        
        # Fallback для вакансий (старая логика)
        title = self._extract_field(user_content, r"Должность:\s*(.+)")
        payment = self._extract_field(user_content, r"Оплата:\s*(.+)")
        location = self._extract_field(user_content, r"Местонахождение:\s*(.+)")
        object_work = self._extract_field(user_content, r"Объект:\s*(.+)")
        conditions = self._extract_field(user_content, r"Условия:\s*(.+)")
        
        # Создаем привлекательный текст
        templates = [
            f"""🚀 Отличная возможность! 

Приглашаем на работу {title.lower()}! 
{f'💰 {payment}' if payment else '💰 Достойная оплата'}
{f'📍 Работаем в {location}' if location else ''}

{f'🏢 {object_work}' if object_work else ''}
{f'⭐ {conditions}' if conditions else ''}

Присоединяйтесь к нашей команде профессионалов! 
Стабильная работа, дружный коллектив, возможности роста.

Ваше будущее начинается сегодня! 🌟""",

            f"""✨ Мечтаете о стабильной работе?

Мы ищем {title.lower()} в нашу команду!
{f'💵 {payment}' if payment else '💵 Конкурентная зарплата'}
{f'🌍 Локация: {location}' if location else ''}

{f'🎯 {object_work}' if object_work else ''}
{f'✅ {conditions}' if conditions else ''}

Работа мечты ждет именно вас!
Дружная атмосфера, профессиональный рост, стабильность.

Откройте новую страницу карьеры! 📈""",

            f"""🎯 Супер предложение!

Требуется {title.lower()}!
{f'💎 {payment}' if payment else '💎 Привлекательная зарплата'}
{f'📌 {location}' if location else ''}

{f'🏭 {object_work}' if object_work else ''}
{f'🌟 {conditions}' if conditions else ''}

Это ваш шанс получить работу мечты!
Профессиональная команда, перспективы развития.

Начните новую главу жизни! 🚀"""
        ]
        
        # Выбираем шаблон на основе хеша title
        template_index = hash(title) % len(templates)
        return templates[template_index].strip()
    
    def _extract_field(self, text: str, pattern: str) -> str:
        """Извлекает поле из текста по регулярному выражению"""
        import re
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def create_assistant_message(self, assistant_id: str, content: str, 
                               max_retries: int = 3) -> Optional[Dict[Any, Any]]:
        """Создание сообщения через OpenAI Assistant API"""
        if not self.api_key:
            fallback_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content}
            ]
            text = self._generate_smart_text(fallback_messages)
            return {'content': text, 'thread_id': None, 'run_id': None}

        try:
            # Создаем thread
            thread_response = self.session.post(
                f"{self.base_url}/threads",
                headers=self.headers,
                json={}
            )
            
            if thread_response.status_code != 200:
                raise Exception(f"Failed to create thread: {thread_response.text}")
            
            thread_id = thread_response.json()['id']
            
            # Добавляем сообщение в thread
            message_response = self.session.post(
                f"{self.base_url}/threads/{thread_id}/messages",
                headers=self.headers,
                json={
                    "role": "user",
                    "content": content
                }
            )
            
            if message_response.status_code != 200:
                raise Exception(f"Failed to add message: {message_response.text}")
            
            # Запускаем assistant
            run_response = self.session.post(
                f"{self.base_url}/threads/{thread_id}/runs",
                headers=self.headers,
                json={
                    "assistant_id": assistant_id
                }
            )
            
            if run_response.status_code != 200:
                raise Exception(f"Failed to run assistant: {run_response.text}")
            
            run_id = run_response.json()['id']
            
            # Ждем завершения
            for _ in range(30):  # 30 секунд максимум
                status_response = self.session.get(
                    f"{self.base_url}/threads/{thread_id}/runs/{run_id}",
                    headers=self.headers
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data['status'] == 'completed':
                        break
                    elif status_data['status'] == 'failed':
                        raise Exception("Assistant run failed")
                time.sleep(1)
            
            # Получаем ответ
            messages_response = self.session.get(
                f"{self.base_url}/threads/{thread_id}/messages",
                headers=self.headers
            )
            
            if messages_response.status_code == 200:
                messages_data = messages_response.json()
                for message in messages_data['data']:
                    if message['role'] == 'assistant':
                        return {
                            'content': message['content'][0]['text']['value'],
                            'thread_id': thread_id,
                            'run_id': run_id
                        }
            
            return None
            
        except Exception as e:
            print(f"Assistant API недоступен: {e}")
            # Fallback на обычный chat completion
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content}
            ]
            text = self._chat_completion(messages)
            return {'content': text, 'thread_id': None, 'run_id': None}
    
    def generate_text_for_video(self, assistant_id: str, prompt: str, context: str = "") -> str:
        full_prompt = f"""
        {prompt}
        
        Контекст: {context}
        
        ВАЖНО: Текст должен быть рассчитан на 40 секунд чтения (примерно 100-120 слов).
        Текст должен быть живым, естественным для озвучки.
        Избегайте сложных терминов и длинных предложений.
        """
        result = self.create_assistant_message(assistant_id, full_prompt)
        return result['content'] if result else ""
    
    def test_connection(self, assistant_id: str) -> bool:
        try:
            self._chat_completion([
                {"role": "user", "content": "say ok"}
            ])
            return True
        except Exception:
            return False
    
    # ========== МЕТОДЫ ДЛЯ ASSISTANT API V2 ==========
    
    @property
    def assistant_headers(self) -> Dict[str, str]:
        """Заголовки для Assistant API с beta версией"""
        if not self.api_key:
            return {"Content-Type": "application/json"}
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        }
    
    def create_thread(self) -> str:
        """Создает новый thread для Assistant API"""
        try:
            response = self.session.post(
                f"{self.base_url}/threads",
                headers=self.assistant_headers,
                json={},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['id']
            else:
                raise Exception(f"Failed to create thread: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Ошибка создания thread: {e}")
            return None
    
    def add_message(self, thread_id: str, content: str) -> str:
        """Добавляет сообщение в thread"""
        try:
            response = self.session.post(
                f"{self.base_url}/threads/{thread_id}/messages",
                headers=self.assistant_headers,
                json={
                    "role": "user",
                    "content": content
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['id']
            else:
                raise Exception(f"Failed to add message: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Ошибка добавления сообщения: {e}")
            return None
    
    def run_assistant(self, thread_id: str, assistant_id: str) -> str:
        """Запускает assistant в thread"""
        try:
            response = self.session.post(
                f"{self.base_url}/threads/{thread_id}/runs",
                headers=self.assistant_headers,
                json={
                    "assistant_id": assistant_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['id']
            else:
                raise Exception(f"Failed to run assistant: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Ошибка запуска assistant: {e}")
            return None
    
    def get_response(self, thread_id: str, run_id: str, timeout: int = 60) -> str:
        """Получает ответ от assistant с ожиданием завершения"""
        try:
            # Ждем завершения run
            for i in range(timeout):
                status_response = self.session.get(
                    f"{self.base_url}/threads/{thread_id}/runs/{run_id}",
                    headers=self.assistant_headers,
                    timeout=30
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data['status']
                    
                    if status == 'completed':
                        # Получаем сообщения
                        messages_response = self.session.get(
                            f"{self.base_url}/threads/{thread_id}/messages",
                            headers=self.assistant_headers,
                            timeout=30
                        )
                        
                        if messages_response.status_code == 200:
                            messages = messages_response.json()['data']
                            if messages:
                                # Находим последнее сообщение от assistant
                                for msg in messages:
                                    if msg['role'] == 'assistant':
                                        return msg['content'][0]['text']['value']
                        break
                    elif status == 'failed':
                        raise Exception("Assistant run failed")
                
                time.sleep(1)
            
            raise Exception(f"Timeout waiting for assistant response ({timeout}s)")
        except Exception as e:
            print(f"❌ Ошибка получения ответа: {e}")
            return None
    
    def rewrite_with_assistant(self, transcript: str, assistant_id: str) -> str:
        """Переписывает текст через Assistant API с fallback"""
        with open('/var/www/gsr-content-factory/debug.log', 'a') as f:
            f.write(f"🔍 DEBUG: api_key={self.api_key[:20]}..., assistant_id={assistant_id}\n")
        
        if not self.api_key or not assistant_id:
            with open('/var/www/gsr-content-factory/debug.log', 'a') as f:
                f.write(f"⚠️ Fallback: api_key={bool(self.api_key)}, assistant_id={bool(assistant_id)}\n")
            # Fallback на старый метод
            return self._chat_completion([
                {"role": "user", "content": f"Перепиши этот текст для Instagram Reels, сделай его более привлекательным и вирусным:\n\n{transcript}"}
            ])
        
        try:
            # Создаем thread
            thread_id = self.create_thread()
            if not thread_id:
                raise Exception("Failed to create thread")
            
            # Добавляем сообщение
            message_id = self.add_message(thread_id, transcript)
            if not message_id:
                raise Exception("Failed to add message")
            
            # Запускаем assistant
            run_id = self.run_assistant(thread_id, assistant_id)
            if not run_id:
                raise Exception("Failed to run assistant")
            
            # Получаем ответ
            response = self.get_response(thread_id, run_id, timeout=60)
            if response:
                return response
            else:
                raise Exception("Failed to get response")
                
        except Exception as e:
            print(f"❌ Assistant API failed: {e}, falling back to chat completion")
            # Fallback на старый метод
            return self._chat_completion([
                {"role": "user", "content": f"Перепиши этот текст для Instagram Reels, сделай его более привлекательным и вирусным:\n\n{transcript}"}
            ])