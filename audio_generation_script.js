// Обновленная функция генерации аудио с настройками голоса
function generateAudio() {
    const statusDiv = document.getElementById('audioStatus');
    const resultDiv = document.getElementById('audioResult');
    const audioSource = document.getElementById('audioSource');
    
    // Получаем настройки голоса
    const voiceId = document.getElementById('audioVoiceId').value;
    const modelId = document.getElementById('audioModelId').value;
    const speed = parseFloat(document.getElementById('audioSpeed').value);
    const stability = parseFloat(document.getElementById('audioStability').value);
    const similarity = parseFloat(document.getElementById('audioSimilarity').value);
    
    // Получаем текст из шага 4
    const rewrittenText = document.getElementById('rewrittenText').value;
    if (!rewrittenText.trim()) {
        statusDiv.innerHTML = '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i>Сначала перепишите текст на шаге 4</div>';
        return;
    }
    
    statusDiv.innerHTML = '<div class="alert alert-info"><i class="fas fa-spinner fa-spin me-2"></i>Генерируем аудио с настройками голоса...</div>';
    
    // Отправляем запрос с полными настройками
    fetch('/api/trends/generate-audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: rewrittenText,
            voice_id: voiceId,
            model_id: modelId,
            speed: speed,
            stability: stability,
            similarity_boost: similarity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusDiv.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i>Аудио создано!</div>';
            
            // Загружаем аудио в плеер
            audioSource.src = data.audio_url;
            resultDiv.style.display = 'block';
            
            // Обновляем статус шага
            document.getElementById('step5').classList.remove('step-disabled');
            document.getElementById('step5').classList.add('step-completed');
            
        } else {
            statusDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>Ошибка: ' + data.message + '</div>';
        }
    })
    .catch(error => {
        console.error('Audio generation error:', error);
        statusDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>Ошибка подключения: ' + error.message + '</div>';
    });
}

// Инициализация слайдеров
document.addEventListener('DOMContentLoaded', function() {
    // Обновление значений слайдеров
    document.getElementById('audioSpeed').addEventListener('input', function() {
        document.getElementById('speedValue').textContent = this.value + 'x';
    });
    
    document.getElementById('audioStability').addEventListener('input', function() {
        document.getElementById('stabilityValue').textContent = this.value;
    });
    
    document.getElementById('audioSimilarity').addEventListener('input', function() {
        document.getElementById('similarityValue').textContent = this.value;
    });
});
