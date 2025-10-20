// ИСПРАВЛЕННАЯ функция настройки аудио плеера
function setupEnhancedAudioPlayer(audioUrl) {
    console.log('🎵 Настройка аудио плеера:', audioUrl);
    
    const audioResult = document.getElementById('audioResult');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioSource = document.getElementById('audioSource');
    
    // Показываем результат
    audioResult.style.display = 'block';
    
    // ОСТАНОВЛЯЕМ текущее воспроизведение
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    
    // Устанавливаем источник
    audioSource.src = audioUrl;
    
    // Ждем загрузки метаданных ПЕРЕД перезагрузкой
    audioPlayer.addEventListener('loadedmetadata', function() {
        console.log('✅ Метаданные загружены, готов к воспроизведению');
    }, { once: true });
    
    audioPlayer.addEventListener('canplay', function() {
        console.log('✅ Аудио готово к воспроизведению');
    }, { once: true });
    
    audioPlayer.addEventListener('error', function(e) {
        console.error('❌ Ошибка загрузки аудио:', e);
        alert('Ошибка загрузки аудио. Попробуйте обновить страницу.');
    }, { once: true });
    
    // БЕЗОПАСНАЯ перезагрузка
    try {
        audioPlayer.load();
    } catch (e) {
        console.error('Ошибка load():', e);
    }
    
    console.log('✅ Аудио плеер настроен');
}
