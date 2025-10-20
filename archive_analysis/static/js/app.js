// Основной JavaScript для приложения
class ContentFactory {
    constructor() {
        this.socket = io();
        this.currentTasks = new Map();
        this.init();
    }

    init() {
        this.setupSocketListeners();
        this.setupEventListeners();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('task_update', (data) => {
            this.updateTaskProgress(data);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
    }

    setupEventListeners() {
        // Обработчики для форм генерации
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-generate')) {
                this.handleGenerateClick(e);
            }
        });

        // Обработчики для модальных окон
        document.addEventListener('shown.bs.modal', (e) => {
            if (e.target.id === 'resultModal') {
                this.handleResultModalShown(e);
            }
        });
    }

    async handleGenerateClick(e) {
        e.preventDefault();
        const button = e.target;
        const form = button.closest('form');
        const module = button.dataset.module;

        if (!module) {
            this.showError('Модуль не определен');
            return;
        }

        // Отключаем кнопку
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Генерация...';

        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            const response = await fetch(`/api/generate/${module}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.startTaskTracking(result.task_id, module);
                this.showProgressToast();
            } else {
                this.showError(result.message || 'Ошибка при запуске генерации');
            }
        } catch (error) {
            this.showError('Ошибка сети: ' + error.message);
        } finally {
            // Восстанавливаем кнопку через несколько секунд
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-play me-2"></i>Запустить генерацию';
            }, 3000);
        }
    }

    startTaskTracking(taskId, module) {
        this.currentTasks.set(taskId, { module, startTime: Date.now() });
        this.socket.emit('join_task', { task_id: taskId });
        this.pollTaskStatus(taskId);
    }

    async pollTaskStatus(taskId) {
        try {
            const response = await fetch(`/api/task/${taskId}`);
            const data = await response.json();

            this.updateTaskProgress(data);

            // Продолжаем опрос, если задача не завершена
            if (data.status === 'processing' || data.status === 'pending') {
                setTimeout(() => this.pollTaskStatus(taskId), 2000);
            }
        } catch (error) {
            console.error('Error polling task status:', error);
        }
    }

    updateTaskProgress(data) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const toast = document.getElementById('progressToast');

        if (progressBar) {
            progressBar.style.width = `${data.progress}%`;
            progressBar.setAttribute('aria-valuenow', data.progress);
        }

        if (progressText) {
            progressText.textContent = data.current_step || data.step || 'Обработка...';
        }

        // Обновляем класс прогресс-бара в зависимости от статуса
        if (progressBar) {
            progressBar.className = 'progress-bar';
            if (data.status === 'completed') {
                progressBar.classList.add('bg-success');
            } else if (data.status === 'failed') {
                progressBar.classList.add('bg-danger');
            } else {
                progressBar.classList.add('bg-primary');
            }
        }

        // Если задача завершена
        if (data.status === 'completed') {
            this.hideProgressToast();
            this.showResult(data.result_data);
        } else if (data.status === 'failed') {
            this.hideProgressToast();
            this.showError(data.error_message || 'Произошла ошибка при генерации');
        }
    }

    showProgressToast() {
        const toast = new bootstrap.Toast(document.getElementById('progressToast'));
        toast.show();
    }

    hideProgressToast() {
        const toast = bootstrap.Toast.getInstance(document.getElementById('progressToast'));
        if (toast) {
            toast.hide();
        }
    }

    showResult(resultData) {
        const modal = new bootstrap.Modal(document.getElementById('resultModal'));
        const content = document.getElementById('resultContent');

        if (resultData) {
            content.innerHTML = this.formatResult(resultData);
        } else {
            content.innerHTML = '<p>Генерация завершена успешно!</p>';
        }

        modal.show();
    }

    formatResult(data) {
        let html = '<div class="result-content">';

        if (data.video_url) {
            html += `
                <div class="mb-3">
                    <h6>Готовое видео:</h6>
                    <div class="d-flex align-items-center">
                        <div class="video-thumbnail me-3">
                            <i class="fas fa-video"></i>
                        </div>
                        <div>
                            <a href="${data.video_url}" target="_blank" class="btn btn-primary btn-sm">
                                <i class="fas fa-download me-2"></i>Скачать видео
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }

        if (data.text) {
            html += `
                <div class="mb-3">
                    <h6>Сгенерированный текст:</h6>
                    <div class="p-3 bg-light rounded">
                        <p class="mb-0">${data.text}</p>
                    </div>
                </div>
            `;
        }

        if (data.audio_url) {
            html += `
                <div class="mb-3">
                    <h6>Аудиофайл:</h6>
                    <audio controls class="w-100">
                        <source src="${data.audio_url}" type="audio/mpeg">
                        Ваш браузер не поддерживает аудио элемент.
                    </audio>
                </div>
            `;
        }

        // Дополнительная информация в зависимости от модуля
        if (data.viral_posts_analyzed) {
            html += `
                <div class="mb-3">
                    <small class="text-muted">
                        Проанализировано ${data.viral_posts_analyzed} вирусных постов
                    </small>
                </div>
            `;
        }

        if (data.total_vacancies_processed) {
            html += `
                <div class="mb-3">
                    <small class="text-muted">
                        Обработано ${data.total_vacancies_processed} вакансий
                    </small>
                </div>
            `;
        }

        if (data.total_topics_processed) {
            html += `
                <div class="mb-3">
                    <small class="text-muted">
                        Создано видео по ${data.total_topics_processed} темам
                    </small>
                </div>
            `;
        }

        html += '</div>';
        return html;
    }

    showError(message) {
        // Создаем временный алерт
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Добавляем в начало контейнера
        const container = document.querySelector('main.container');
        container.insertAdjacentHTML('afterbegin', alertHtml);

        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }

    showSuccess(message) {
        const alertHtml = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const container = document.querySelector('main.container');
        container.insertAdjacentHTML('afterbegin', alertHtml);

        setTimeout(() => {
            const alert = container.querySelector('.alert-success');
            if (alert) {
                alert.remove();
            }
        }, 3000);
    }
}

// Утилиты для работы с формами
class FormUtils {
    static async saveSettings(moduleName, formData) {
        try {
            const response = await fetch(`/api/settings/${moduleName}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            return result;
        } catch (error) {
            throw new Error('Ошибка сети: ' + error.message);
        }
    }

    static async loadVoices() {
        try {
            const response = await fetch('/api/voices');
            return await response.json();
        } catch (error) {
            console.error('Error loading voices:', error);
            return [];
        }
    }

    static async loadAvatars() {
        try {
            const response = await fetch('/api/avatars');
            return await response.json();
        } catch (error) {
            console.error('Error loading avatars:', error);
            return [];
        }
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    window.contentFactory = new ContentFactory();
    window.formUtils = FormUtils;

    // Инициализация Bootstrap компонентов
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Функции для быстрых действий
window.generateAll = function() {
    if (confirm('Запустить генерацию во всех модулях? Это может занять продолжительное время.')) {
        // Логика запуска всех модулей
        console.log('Starting all modules...');
    }
};

window.checkStatus = function() {
    // Логика проверки статуса
    console.log('Checking status...');
};

window.viewHistory = function() {
    // Логика просмотра истории
    console.log('Viewing history...');
};

window.clearCache = function() {
    if (confirm('Вы уверены, что хотите очистить кэш?')) {
        // Логика очистки кэша
        console.log('Clearing cache...');
        window.contentFactory.showSuccess('Кэш очищен');
    }
};
