import requests
import time
import json
import os
from typing import Optional, Dict, Any
from config import Config

class OpenAIClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.session = requests.Session()
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _chat_completion(self, messages: list) -> str:
        """Прямой вызов OpenAI API с Assistant"""
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
        """Генерирует умный текст на основе данных вакансии"""
        import re
        
        # Извлекаем данные из промпта
        user_content = ""
        for message in messages:
            if message["role"] == "user":
                user_content = message["content"]
                break
        
        # Парсим данные вакансии
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
