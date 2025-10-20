// Улучшенная функция генерации аудио с лучшим плеером
async function generateAudioAdvanced() {
    console.log('🔊 Генерация аудио с настройками...');
    const statusDiv = document.getElementById('audioStatus');
    const audioResult = document.getElementById('audioResult');
    
    // Получаем текст из шага 4
    const rewrittenText = document.getElementById('rewrittenText');
    if (!rewrittenText || !rewrittenText.textContent.trim()) {
        statusDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Сначала перепишите текст на шаге 4
            </div>`;
        return;
    }
    
    const text = rewrittenText.textContent.trim();
    
    // Получаем настройки
    const voiceId = document.getElementById('voiceSelect').value;
    const modelId = document.getElementById('modelSelect').value;
    const speed = parseFloat(document.getElementById('speedSlider').value);
    const stability = parseFloat(document.getElementById('stabilitySlider').value);
    const similarity = parseFloat(document.getElementById('similaritySlider').value);
    
    statusDiv.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-spinner fa-spin me-2"></i>
            Создаем аудио с настройками: голос=${voiceId}, модель=${modelId}, скорость=${speed}...
        </div>`;
    
    try {
        const response = await fetch('/api/trends/generate-audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                voice_id: voiceId,
                model_id: modelId,
                speed: speed,
                stability: stability,
                similarity_boost: similarity
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Аудио создано успешно!
                </div>`;
            
            // Показываем результат
            audioResult.style.display = 'block';
            
            // Настраиваем улучшенный плеер
            setupEnhancedAudioPlayer(result.audio_url);
            
            // Активируем следующий шаг
            activateStep6();
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Ошибка генерации: ${result.message || 'Неизвестная ошибка'}
                </div>`;
        }
    } catch (error) {
        console.error('Ошибка генерации аудио:', error);
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Ошибка генерации: ${error.message}
            </div>`;
    }
}

// Улучшенная функция настройки аудио плеера
function setupEnhancedAudioPlayer(audioUrl) {
    console.log('🎵 Настройка улучшенного аудио плеера:', audioUrl);
    
    // Обновляем HTML плеера
    const audioResult = document.getElementById('audioResult');
    audioResult.innerHTML = `
        <h5 class="gsr-text-primary">Сгенерированное аудио:</h5>
        
        <!-- Основной HTML5 плеер -->
        <audio controls class="w-100 mb-3" id="audioPlayer" preload="metadata">
            <source id="audioSource" src="${audioUrl}" type="audio/mpeg">
            <source id="audioSourceOgg" src="${audioUrl.replace('.mp3', '.ogg')}" type="audio/ogg">
            Ваш браузер не поддерживает аудио элемент.
        </audio>
        
        <!-- Альтернативный плеер для Chrome -->
        <div id="chromePlayer" class="d-none">
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                <strong>Chrome плеер:</strong>
                <button class="btn btn-sm btn-primary ms-2" onclick="playChromeAudio()">
                    <i class="fas fa-play me-1"></i>Воспроизвести
                </button>
                <button class="btn btn-sm btn-secondary ms-1" onclick="pauseChromeAudio()">
                    <i class="fas fa-pause me-1"></i>Пауза
                </button>
            </div>
        </div>
        
        <!-- Ссылка для скачивания -->
        <div class="mt-2">
            <a href="${audioUrl}" class="btn btn-outline-primary btn-sm" download>
                <i class="fas fa-download me-1"></i>Скачать аудио
            </a>
        </div>
        
        <!-- Информация о файле -->
        <div class="mt-2 text-muted small">
            <span id="audioInfo">Готово к воспроизведению</span>
        </div>
    `;
    
    // Настраиваем плеер
    const audioPlayer = document.getElementById('audioPlayer');
    const audioInfo = document.getElementById('audioInfo');
    const chromePlayer = document.getElementById('chromePlayer');
    
    // Проверяем поддержку браузера
    const isChrome = /Chrome/.test(navigator.userAgent);
    
    if (isChrome) {
        console.log('🔧 Chrome обнаружен - показываем альтернативный плеер');
        chromePlayer.classList.remove('d-none');
    }
    
    // Обработчики событий
    audioPlayer.addEventListener('loadedmetadata', function() {
        console.log('✅ Метаданные аудио загружены');
        audioInfo.textContent = `Длительность: ${Math.round(audioPlayer.duration)} сек`;
    });
    
    audioPlayer.addEventListener('error', function(e) {
        console.error('❌ Ошибка загрузки аудио:', e);
        audioInfo.textContent = 'Ошибка загрузки аудио. Попробуйте скачать файл.';
        
        if (isChrome) {
            chromePlayer.classList.remove('d-none');
        }
    });
    
    // Принудительная перезагрузка
    audioPlayer.load();
    
    // Сохраняем URL для глобального доступа
    window.currentAudioUrl = audioUrl;
}

// Функции для Chrome плеера
function playChromeAudio() {
    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.play().catch(e => {
        console.error('Ошибка воспроизведения:', e);
        alert('Не удалось воспроизвести аудио. Попробуйте скачать файл.');
    });
}

function pauseChromeAudio() {
    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.pause();
}
