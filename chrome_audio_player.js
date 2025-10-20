// Chrome-совместимый аудио плеер
function setupEnhancedAudioPlayer(audioUrl) {
    console.log('🎵 Настройка аудио плеера для Chrome:', audioUrl);
    
    const audioResult = document.getElementById('audioStatus');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioSource = document.getElementById('audioSource');
    
    // Показываем результат
    if (audioResult) {
        audioResult.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Загружаем аудио для Chrome: ${audioUrl}
            </div>`;
    }
    
    // Очищаем предыдущие обработчики
    audioPlayer.removeEventListener('loadedmetadata', handleLoadedMetadata);
    audioPlayer.removeEventListener('canplay', handleCanPlay);
    audioPlayer.removeEventListener('error', handleError);
    
    // Добавляем новые обработчики
    audioPlayer.addEventListener('loadedmetadata', handleLoadedMetadata);
    audioPlayer.addEventListener('canplay', handleCanPlay);
    audioPlayer.addEventListener('error', handleError);
    
    // Устанавливаем источник
    audioSource.src = audioUrl;
    
    // Принудительная загрузка
    audioPlayer.load();
    
    function handleLoadedMetadata() {
        console.log('✅ Метаданные загружены');
        if (audioResult) {
            audioResult.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Аудио загружено! Длительность: ${Math.round(audioPlayer.duration)} сек
                </div>`;
        }
    }
    
    function handleCanPlay() {
        console.log('✅ Аудио готово к воспроизведению');
    }
    
    function handleError(e) {
        console.error('❌ Ошибка загрузки аудио:', e);
        if (audioResult) {
            audioResult.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Ошибка загрузки аудио: ${e.message || 'Неизвестная ошибка'}
                </div>`;
        }
    }
    
    console.log('✅ Chrome-совместимый аудио плеер настроен');
}

// БЕЗОПАСНАЯ функция воспроизведения для Chrome
function playAudioSafely() {
    const audioPlayer = document.getElementById('audioPlayer');
    
    // Проверяем что аудио загружено
    if (audioPlayer.readyState < 2) {
        console.log('⏳ Аудио еще загружается...');
        return;
    }
    
    // Безопасное воспроизведение
    const playPromise = audioPlayer.play();
    
    if (playPromise !== undefined) {
        playPromise.then(() => {
            console.log('✅ Воспроизведение началось');
        }).catch(error => {
            console.error('❌ Ошибка воспроизведения:', error);
        });
    }
}
