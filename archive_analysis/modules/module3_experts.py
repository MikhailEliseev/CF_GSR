from celery_app import celery_app
from modules.base_module import BaseModule
from models import db, ExpertTopics
from typing import List, Dict, Any


class ExpertModule(BaseModule):
    """
    Модуль генерации экспертного контента
    """

    def __init__(self):
        super().__init__('experts')

    def prepare_context(self, topic: str = None, consumer_profile: str = None) -> str:
        if not consumer_profile:
            additional_settings = self.settings.get_additional_settings()
            consumer_profile = additional_settings.get('consumer_profile', 'Общая аудитория')

        if not topic:
            return f"Создайте экспертный контент для аудитории: {consumer_profile}"

        context = f"""
        Создайте экспертный контент на тему: "{topic}"

        Портрет потребителя: {consumer_profile}

        Требования к контенту:
        1. Экспертная подача материала
        2. Практические советы и рекомендации
        3. Понятный язык для целевой аудитории
        4. Вовлекающая подача
        5. Ценная информация
        6. Мотивирующий финал

        Структура должна включать:
        - Захватывающее вступление
        - Основную ценность/совет
        - Практический пример или кейс
        - Призыв к действию
        """

        return context

    def generate_topics(self, session_id: str, num_topics: int = 15) -> List[str]:
        if not self.openai_service or not self.settings.openai_assistant_id:
            raise Exception("OpenAI client or assistant ID not configured")

        additional_settings = self.settings.get_additional_settings()
        consumer_profile = additional_settings.get('consumer_profile', 'Общая аудитория')

        prompt = f"""
        Сгенерируйте {num_topics} актуальных тем для экспертного контента.

        Портрет потребителя: {consumer_profile}

        Требования к темам:
        1. Актуальные и интересные для целевой аудитории
        2. Позволяют дать экспертные советы
        3. Имеют практическую ценность
        4. Подходят для 40-секундного видео
        5. Вызывают интерес и желание узнать больше

        Форматируйте ответ как пронумерованный список тем, каждая тема на новой строке.
        Пример:
        1. Как увеличить продуктивность на 200% за 7 дней
        2. 5 ошибок в карьере, которые стоят вам повышения
        ...
        """

        try:
            result = self.openai_service.create_assistant_message(
                self.settings.openai_assistant_id,
                prompt
            )

            if not result:
                raise Exception("Failed to generate topics")

            topics_text = result.get('content') if isinstance(result, dict) else str(result)
            topics = []
            for line in topics_text.split('\n'):
                line = line.strip()
                if line and any(line.startswith(str(i) + '.') for i in range(1, 100)):
                    topic = line.split('.', 1)[1].strip()
                    topics.append(topic)

            if not topics:
                topics = [f"Тема #{i}" for i in range(1, num_topics + 1)]

            for topic in topics:
                expert_topic = ExpertTopics(
                    session_id=session_id,
                    topic=topic,
                    is_selected=False
                )
                db.session.add(expert_topic)

            db.session.commit()
            return topics

        except Exception as e:
            raise Exception(f"Error generating topics: {e}")

    def get_session_topics(self, session_id: str) -> List[Dict[str, Any]]:
        topics = ExpertTopics.query.filter_by(session_id=session_id).all()
        return [
            {
                'id': topic.id,
                'topic': topic.topic,
                'is_selected': topic.is_selected
            }
            for topic in topics
        ]

    def update_topic_selection(self, topic_ids: List[int]):
        if topic_ids:
            first_topic = ExpertTopics.query.get(topic_ids[0])
            if first_topic:
                ExpertTopics.query.filter_by(session_id=first_topic.session_id).update({
                    'is_selected': False
                })

        ExpertTopics.query.filter(ExpertTopics.id.in_(topic_ids)).update({
            'is_selected': True
        }, synchronize_session=False)

        db.session.commit()

    @celery_app.task(bind=True)
    def start_generation(self, task_id: str, selected_topic_ids: List[int],
                         voice_id: str = None, avatar_id: str = None):
        try:
            module = ExpertModule()

            additional_settings = module.settings.get_additional_settings()
            if not voice_id:
                voice_id = additional_settings.get('default_voice_id')
            if not avatar_id:
                avatar_id = additional_settings.get('default_avatar_id')

            if not voice_id or not avatar_id:
                raise Exception("Voice ID and Avatar ID must be specified")

            module.update_task_progress(task_id, 5, "Загрузка выбранных тем...")

            selected_topics = ExpertTopics.query.filter(
                ExpertTopics.id.in_(selected_topic_ids)
            ).all()

            if not selected_topics:
                raise Exception("No topics selected")

            consumer_profile = additional_settings.get('consumer_profile', 'Общая аудитория')
            results = []

            total_topics = len(selected_topics)

            for i, topic_obj in enumerate(selected_topics):
                current_progress = 10 + (i * 80 // total_topics)

                module.update_task_progress(
                    task_id,
                    current_progress,
                    f"Создание контента {i+1}/{total_topics}: {topic_obj.topic[:50]}..."
                )

                context = module.prepare_context(topic_obj.topic, consumer_profile)

                try:
                    result = module.execute_full_pipeline(
                        f"{task_id}_topic_{i}",
                        context,
                        voice_id,
                        avatar_id
                    )
                    result['topic'] = topic_obj.topic
                    result['topic_id'] = topic_obj.id
                    results.append(result)

                except Exception as e:
                    print(f"Error processing topic {i}: {e}")
                    continue

            final_result = {
                'total_topics_processed': len(results),
                'consumer_profile': consumer_profile,
                'generated_videos': results
            }

            module.update_task_progress(task_id, 100, "Готово!", result_data=final_result)

            return final_result

        except Exception as e:
            module = ExpertModule()
            module.update_task_progress(task_id, 0, "Ошибка", error_message=str(e))
            raise e

    @celery_app.task(bind=True)
    def generate_single_topic(self, task_id: str, topic: str,
                              voice_id: str = None, avatar_id: str = None):
        try:
            module = ExpertModule()

            additional_settings = module.settings.get_additional_settings()
            if not voice_id:
                voice_id = additional_settings.get('default_voice_id')
            if not avatar_id:
                avatar_id = additional_settings.get('default_avatar_id')

            consumer_profile = additional_settings.get('consumer_profile', 'Общая аудитория')

            context = module.prepare_context(topic, consumer_profile)

            result = module.execute_full_pipeline(task_id, context, voice_id, avatar_id)
            result['topic'] = topic
            result['consumer_profile'] = consumer_profile

            return result

        except Exception as e:
            module = ExpertModule()
            module.update_task_progress(task_id, 0, "Ошибка", error_message=str(e))
            raise e

    def test_integrations(self) -> Dict[str, bool]:
        results = {}

        results['openai'] = self.openai_service.test_connection(self.settings.openai_assistant_id) if self.openai_service else False
        results['elevenlabs'] = self.elevenlabs_service.test_connection() if self.elevenlabs_service else False
        results['heygen'] = self.heygen_service.test_connection() if self.heygen_service else False
        results['storage'] = self.storage_client.test_connection()

        return results
