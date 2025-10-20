// Быстрое исправление 504 ошибки в интерфейсе
// Добавить этот код в JavaScript интерфейса

function collectReelsWithTimeout() {
    const statusDiv = document.getElementById('reelsStatus');
    const selectedCompetitors = getSelectedCompetitors();
    const reelsCount = parseInt(document.getElementById('reelsCount').value) || 5;
    
    // Ограничиваем количество рилсов для избежания таймаута
    const safeCount = Math.min(reelsCount, 5);
    
    statusDiv.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-spinner fa-spin me-2"></i>
            Собираем ${safeCount} рилсов (ограничено для избежания таймаута)...
        </div>
    `;
    
    // Создаем AbortController с увеличенным таймаутом
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
        controller.abort();
        statusDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-clock me-2"></i>
                Таймаут! Попробуйте меньше рилсов (1-3) или проверьте подключение
            </div>
        `;
    }, 60000); // 60 секунд вместо 30
    
    fetch('/api/trends/collect-reels', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            competitors: selectedCompetitors,
            count: safeCount  // Используем ограниченное количество
        }),
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            if (response.status === 504) {
                throw new Error('Сервер не отвечает. Попробуйте меньше рилсов (1-3)');
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    })
    .then(result => {
        if (result.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Успешно собрано ${result.total_count || 0} рилсов
                    <br><small>Виральных: ${result.viral_count || 0}</small>
                </div>
            `;
            
            // Активируем следующий шаг
            activateStep2();
            updateReelsStats(result);
            
        } else {
            throw new Error(result.message || 'Неизвестная ошибка');
        }
    })
    .catch(error => {
        clearTimeout(timeoutId);
        console.error('Reels collection error:', error);
        
        if (error.name === 'AbortError') {
            statusDiv.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-clock me-2"></i>
                    Таймаут! Apify API работает медленно.<br>
                    <strong>Рекомендации:</strong><br>
                    • Попробуйте 1-3 рилса<br>
                    • Проверьте интернет-соединение<br>
                    • Попробуйте позже
                </div>
            `;
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Ошибка: ${error.message}
                </div>
            `;
        }
    });
}

// Функция для получения выбранных конкурентов
function getSelectedCompetitors() {
    const checkboxes = document.querySelectorAll('input[name="competitor"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Функция для активации шага 2
function activateStep2() {
    const step2 = document.getElementById('step2');
    if (step2) {
        step2.classList.remove('step-disabled');
        step2.classList.add('step-completed');
    }
}

// Функция для обновления статистики
function updateReelsStats(result) {
    const totalElement = document.getElementById('totalReels');
    const collectedElement = document.getElementById('collectedReels');
    
    if (totalElement) totalElement.textContent = result.total_count || 0;
    if (collectedElement) collectedElement.textContent = result.viral_count || 0;
}
