import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from models import db, TrendAnalysis, CompetitorData, ContentGeneration

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trends_module.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('trends_module')

class TrendsMonitoring:
    """Мониторинг и аналитика для модуля трендвотчинга"""
    
    def __init__(self):
        self.logger = logger
    
    def log_analysis_start(self, analysis_id: int, config: Dict) -> None:
        """Логирование начала анализа"""
        self.logger.info(f"Analysis {analysis_id} started with config: {config}")
    
    def log_analysis_completion(self, analysis_id: int, results: Dict) -> None:
        """Логирование завершения анализа"""
        self.logger.info(f"Analysis {analysis_id} completed with results: {results}")
    
    def log_analysis_error(self, analysis_id: int, error: str) -> None:
        """Логирование ошибки анализа"""
        self.logger.error(f"Analysis {analysis_id} failed: {error}")
    
    def log_api_call(self, service: str, endpoint: str, status: str, duration: float) -> None:
        """Логирование вызовов API"""
        self.logger.info(f"API call to {service}/{endpoint}: {status} ({duration:.2f}s)")
    
    def get_analysis_stats(self, days_back: int = 7) -> Dict[str, Any]:
        """Получение статистики анализов"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Общая статистика
            total_analyses = TrendAnalysis.query.filter(
                TrendAnalysis.created_at >= cutoff_date
            ).count()
            
            completed_analyses = TrendAnalysis.query.filter(
                TrendAnalysis.created_at >= cutoff_date,
                TrendAnalysis.status == 'completed'
            ).count()
            
            failed_analyses = TrendAnalysis.query.filter(
                TrendAnalysis.created_at >= cutoff_date,
                TrendAnalysis.status == 'failed'
            ).count()
            
            # Статистика по конкурентам
            total_competitors = CompetitorData.query.join(TrendAnalysis).filter(
                TrendAnalysis.created_at >= cutoff_date
            ).count()
            
            viral_posts = CompetitorData.query.join(TrendAnalysis).filter(
                TrendAnalysis.created_at >= cutoff_date,
                CompetitorData.views >= 25000
            ).count()
            
            # Статистика генерации контента
            total_generations = ContentGeneration.query.join(TrendAnalysis).filter(
                TrendAnalysis.created_at >= cutoff_date
            ).count()
            
            completed_generations = ContentGeneration.query.join(TrendAnalysis).filter(
                TrendAnalysis.created_at >= cutoff_date,
                ContentGeneration.status == 'completed'
            ).count()
            
            return {
                'period_days': days_back,
                'analyses': {
                    'total': total_analyses,
                    'completed': completed_analyses,
                    'failed': failed_analyses,
                    'success_rate': (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0
                },
                'competitors': {
                    'total_posts': total_competitors,
                    'viral_posts': viral_posts,
                    'viral_rate': (viral_posts / total_competitors * 100) if total_competitors > 0 else 0
                },
                'content_generation': {
                    'total': total_generations,
                    'completed': completed_generations,
                    'success_rate': (completed_generations / total_generations * 100) if total_generations > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting analysis stats: {str(e)}")
            return {}
    
    def get_performance_metrics(self, hours_back: int = 24) -> Dict[str, Any]:
        """Получение метрик производительности"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Время выполнения анализов
            analyses = TrendAnalysis.query.filter(
                TrendAnalysis.created_at >= cutoff_time,
                TrendAnalysis.status == 'completed'
            ).all()
            
            execution_times = []
            for analysis in analyses:
                if analysis.updated_at and analysis.created_at:
                    duration = (analysis.updated_at - analysis.created_at).total_seconds()
                    execution_times.append(duration)
            
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            # Статистика по статусам
            status_counts = {}
            for analysis in TrendAnalysis.query.filter(
                TrendAnalysis.created_at >= cutoff_time
            ).all():
                status = analysis.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'period_hours': hours_back,
                'avg_execution_time_seconds': avg_execution_time,
                'status_distribution': status_counts,
                'total_analyses': len(analyses)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {str(e)}")
            return {}
    
    def get_top_competitors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение топ конкурентов по engagement"""
        try:
            competitors = db.session.query(
                CompetitorData.competitor_handle,
                db.func.avg(CompetitorData.engagement_rate).label('avg_engagement'),
                db.func.count(CompetitorData.id).label('post_count'),
                db.func.avg(CompetitorData.views).label('avg_views')
            ).group_by(CompetitorData.competitor_handle)\
             .order_by(db.func.avg(CompetitorData.engagement_rate).desc())\
             .limit(limit).all()
            
            result = []
            for comp in competitors:
                result.append({
                    'handle': comp.competitor_handle,
                    'avg_engagement': round(comp.avg_engagement, 2),
                    'post_count': comp.post_count,
                    'avg_views': int(comp.avg_views)
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting top competitors: {str(e)}")
            return []
    
    def get_trending_hashtags(self, days_back: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """Получение трендовых хештегов"""
        try:
            # Это упрощенная версия - в реальности нужно парсить хештеги из постов
            # Здесь возвращаем заглушку
            return [
                {'hashtag': '#тренды', 'count': 15, 'engagement': 8.5},
                {'hashtag': '#контент', 'count': 12, 'engagement': 7.2},
                {'hashtag': '#видео', 'count': 10, 'engagement': 6.8},
                {'hashtag': '#соцсети', 'count': 8, 'engagement': 5.9},
                {'hashtag': '#маркетинг', 'count': 6, 'engagement': 4.3}
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting trending hashtags: {str(e)}")
            return []
    
    def check_system_health(self) -> Dict[str, Any]:
        """Проверка здоровья системы"""
        try:
            health_status = {
                'database': 'healthy',
                'apis': {},
                'overall': 'healthy'
            }
            
            # Проверка базы данных
            try:
                db.session.execute('SELECT 1')
                health_status['database'] = 'healthy'
            except Exception as e:
                health_status['database'] = f'error: {str(e)}'
                health_status['overall'] = 'degraded'
            
            # Проверка API ключей
            from config import Config
            api_keys = Config.DEFAULT_API_KEYS
            
            for service, key in api_keys.items():
                if key and key.strip():
                    health_status['apis'][service] = 'configured'
                else:
                    health_status['apis'][service] = 'not_configured'
                    health_status['overall'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {str(e)}")
            return {'overall': 'error', 'error': str(e)}
    
    def cleanup_old_data(self, days_back: int = 30) -> Dict[str, int]:
        """Очистка старых данных"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Удаляем старые анализы
            old_analyses = TrendAnalysis.query.filter(
                TrendAnalysis.created_at < cutoff_date,
                TrendAnalysis.status.in_(['completed', 'failed'])
            ).all()
            
            deleted_count = 0
            for analysis in old_analyses:
                # Удаляем связанные данные
                CompetitorData.query.filter_by(analysis_id=analysis.id).delete()
                ContentGeneration.query.filter_by(analysis_id=analysis.id).delete()
                db.session.delete(analysis)
                deleted_count += 1
            
            db.session.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} old analyses")
            return {'deleted_analyses': deleted_count}
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")
            db.session.rollback()
            return {'error': str(e)}

# Глобальный экземпляр мониторинга
trends_monitoring = TrendsMonitoring()
