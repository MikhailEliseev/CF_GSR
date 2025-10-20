// РАБОЧИЙ аудио плеер без конфликтов
function setupEnhancedAudioPlayer(audioUrl) {
    console.log('🎵 Настройка аудио плеера:', audioUrl);
    
    const audioResult = document.getElementById('audioResult');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioSource = document.getElementById('audioSource');
    
    // Показываем результат
    audioResult.style.display = 'block';
    
    // Устанавливаем источник БЕЗ перезагрузки
    audioSource.src = audioUrl;
    
    // Обработчики событий
    audioPlayer.addEventListener('loadedmetadata', function() {
        console.log('✅ Метаданные загружены');
    }, { once: true });
    
    audioPlayer.addEventListener('canplay', function() {
        console.log('✅ Аудио готово к воспроизведению');
    }, { once: true });
    
    audioPlayer.addEventListener('error', function(e) {
        console.error('❌ Ошибка загрузки аудио:', e);
        alert('Ошибка загрузки аудио. Попробуйте обновить страницу.');
    }, { once: true });
    
    console.log('✅ Аудио плеер настроен');
}

// БЕЗОПАСНАЯ функция воспроизведения
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
