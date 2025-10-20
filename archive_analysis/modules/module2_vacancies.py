from celery_app import celery_app
from modules.base_module import BaseModule
import pandas as pd
import requests
from typing import List, Dict, Any
import io

class VacancyModule(BaseModule):
    """
    Модуль работы с вакансиями
    """
    
    def __init__(self):
        super().__init__('vacancies')
    
    def get_google_sheets_data(self, sheet_url: str) -> pd.DataFrame:
        """
        Получение данных из Google Sheets
        """
        # Преобразуем URL для экспорта в CSV
        if '/edit' in sheet_url:
            csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
            csv_url = csv_url.replace('/edit?pli=1&gid=', '/export?format=csv&gid=')
        else:
            csv_url = sheet_url
        
        try:
            response = requests.get(csv_url)
            response.raise_for_status()
            
            # Читаем CSV данные
            df = pd.read_csv(io.StringIO(response.text))
            return df
            
        except Exception as e:
            raise Exception(f"Error reading Google Sheets: {e}")
    
    def process_vacancy_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Обработка данных вакансий
        """
        vacancies = []
        
        for index, row in df.iterrows():
            # Пропускаем пустые строки
            if pd.isna(row.iloc[0]) or row.iloc[0] == '':
                continue
                
            vacancy = {
                'position': str(row.iloc[0]) if not pd.isna(row.iloc[0]) else '',
                'company': str(row.iloc[1]) if not pd.isna(row.iloc[1]) else '',
                'location': str(row.iloc[2]) if not pd.isna(row.iloc[2]) else '',
                'salary': str(row.iloc[3]) if not pd.isna(row.iloc[3]) else '',
                'conditions': str(row.iloc[4]) if not pd.isna(row.iloc[4]) else '',
                'requirements': str(row.iloc[5]) if not pd.isna(row.iloc[5]) else '',
                'positions_needed': str(row.iloc[6]) if not pd.isna(row.iloc[6]) else '',
                'comments': str(row.iloc[7]) if len(row) > 7 and not pd.isna(row.iloc[7]) else ''
            }
            
            # Фильтруем только вакансии с указанной потребностью
            if vacancy['positions_needed'] and vacancy['positions_needed'] != '0':
                vacancies.append(vacancy)
        
        return vacancies
    
    def prepare_context(self, vacancy: Dict[str, Any] = None) -> str:
        """
        Подготовка контекста для конкретной вакансии
        """
        if not vacancy:
            return "Информация о вакансиях"
        
        context = f"""
        Создайте привлекательный текст для видео-рекламы вакансии:
        
        Должность: {vacancy['position']}
        Компания/Объект: {vacancy['company']}
        Местоположение: {vacancy['location']}
        Заработная плата: {vacancy['salary']}
        Условия работы: {vacancy['conditions']}
        Требования: {vacancy['requirements']}
        Количество мест: {vacancy['positions_needed']}
        Дополнительно: {vacancy['comments']}
        
        Текст должен:
        1. Привлекать внимание к вакансии
        2. Подчеркивать преимущества работы
        3. Мотивировать откликнуться
        4. Быть понятным и дружелюбным
        5. Содержать призыв к действию
        """
        
        return context
    
    def get_vacancies_from_sheets(self) -> List[Dict[str, Any]]:
        """
        Получение актуальных вакансий из Google Sheets
        """
        additional_settings = self.settings.get_additional_settings()
        sheet_url = additional_settings.get('google_sheets_url')
        
        if not sheet_url:
            raise Exception("Google Sheets URL not configured")
        
        df = self.get_google_sheets_data(sheet_url)
        return self.process_vacancy_data(df)
    
    @celery_app.task(bind=True)
    def start_generation(self, task_id: str, vacancy_index: int = None,
                        voice_id: str = None, avatar_id: str = None):
        """
        Запуск генерации для выбранной вакансии или всех вакансий
        """
        try:
            module = VacancyModule()
            
            # Получаем настройки по умолчанию
            additional_settings = module.settings.get_additional_settings()
            if not voice_id:
                voice_id = additional_settings.get('default_voice_id')
            if not avatar_id:
                avatar_id = additional_settings.get('default_avatar_id')
            
            if not voice_id or not avatar_id:
                raise Exception("Voice ID and Avatar ID must be specified")
            
            # Получаем вакансии
            module.update_task_progress(task_id, 5, "Загрузка вакансий...")
            vacancies = module.get_vacancies_from_sheets()
            
            if not vacancies:
                raise Exception("No vacancies found")
            
            results = []
            
            # Если указан индекс конкретной вакансии
            if vacancy_index is not None:
                if vacancy_index >= len(vacancies):
                    raise Exception("Invalid vacancy index")
                
                vacancies_to_process = [vacancies[vacancy_index]]
            else:
                # Обрабатываем все вакансии (ограничиваем до 5 для примера)
                vacancies_to_process = vacancies[:5]
            
            total_vacancies = len(vacancies_to_process)
            
            for i, vacancy in enumerate(vacancies_to_process):
                current_progress = 10 + (i * 80 // total_vacancies)
                
                module.update_task_progress(
                    task_id, 
                    current_progress, 
                    f"Обработка вакансии {i+1}/{total_vacancies}: {vacancy['position']}"
                )
                
                # Подготавливаем контекст для конкретной вакансии
                context = module.prepare_context(vacancy)
                
                # Выполняем пайплайн для этой вакансии
                try:
                    result = module.execute_full_pipeline(
                        f"{task_id}_vacancy_{i}", 
                        context, 
                        voice_id, 
                        avatar_id
                    )
                    result['vacancy_info'] = vacancy
                    results.append(result)
                    
                except Exception as e:
                    print(f"Error processing vacancy {i}: {e}")
                    continue
            
            # Финальный результат
            final_result = {
                'total_vacancies_processed': len(results),
                'total_vacancies_available': len(vacancies),
                'generated_videos': results
            }
            
            module.update_task_progress(task_id, 100, "Готово!", result_data=final_result)
            
            return final_result
            
        except Exception as e:
            module = VacancyModule()
            module.update_task_progress(task_id, 0, "Ошибка", error_message=str(e))
            raise e
    
    def get_vacancies_preview(self) -> List[Dict[str, Any]]:
        """
        Получение превью вакансий для отображения в интерфейсе
        """
        try:
            vacancies = self.get_vacancies_from_sheets()
            # Возвращаем только основную информацию для превью
            return [
                {
                    'index': i,
                    'position': v['position'],
                    'company': v['company'],
                    'salary': v['salary'],
                    'positions_needed': v['positions_needed']
                }
                for i, v in enumerate(vacancies)
            ]
        except Exception as e:
            print(f"Error getting vacancies preview: {e}")
            return []
    
    def test_integrations(self) -> Dict[str, bool]:
        """
        Проверка всех интеграций модуля
        """
        results = {}
        
        # Проверяем доступ к Google Sheets
        try:
            additional_settings = self.settings.get_additional_settings()
            sheet_url = additional_settings.get('google_sheets_url')
            if sheet_url:
                df = self.get_google_sheets_data(sheet_url)
                results['google_sheets'] = len(df) > 0
            else:
                results['google_sheets'] = False
        except Exception:
            results['google_sheets'] = False
        
        # Проверяем остальные интеграции
        if self.openai_service and self.settings.openai_assistant_id:
            results['openai'] = self.openai_service.test_connection(self.settings.openai_assistant_id)
        else:
            results['openai'] = False
        
        if self.elevenlabs_service:
            results['elevenlabs'] = self.elevenlabs_service.test_connection()
        else:
            results['elevenlabs'] = False
        
        if self.heygen_service:
            results['heygen'] = self.heygen_service.test_connection()
        else:
            results['heygen'] = False
        
        results['storage'] = self.storage_client.test_connection()
        
        return results
