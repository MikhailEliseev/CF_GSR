// Простая функция настройки аудио плеера
function setupEnhancedAudioPlayer(audioUrl) {
    console.log('🎵 Настройка аудио плеера:', audioUrl);
    
    const audioResult = document.getElementById('audioResult');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioSource = document.getElementById('audioSource');
    
    // Устанавливаем источник
    audioSource.src = audioUrl;
    
    // Обновляем информацию
    const audioInfo = document.getElementById('audioInfo');
    if (audioInfo) {
        audioInfo.textContent = 'Аудио загружено: ' + audioUrl.split('/').pop();
    }
    
    // Принудительная перезагрузка
    audioPlayer.load();
    
    console.log('✅ Аудио плеер настроен');
}
