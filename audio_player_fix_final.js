// Функция настройки аудио плеера
function setupEnhancedAudioPlayer(audioUrl) {
    console.log('🎵 Настройка аудио плеера:', audioUrl);
    
    const audioResult = document.getElementById('audioResult');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioSource = document.getElementById('audioSource');
    
    // Показываем результат
    audioResult.style.display = 'block';
    
    // Устанавливаем источник
    audioSource.src = audioUrl;
    
    // Принудительная перезагрузка
    audioPlayer.load();
    
    // Обработчики событий
    audioPlayer.addEventListener('loadedmetadata', function() {
        console.log('✅ Метаданные аудио загружены');
    });
    
    audioPlayer.addEventListener('error', function(e) {
        console.error('❌ Ошибка загрузки аудио:', e);
        alert('Ошибка загрузки аудио. Попробуйте обновить страницу.');
    });
    
    console.log('✅ Аудио плеер настроен');
}
