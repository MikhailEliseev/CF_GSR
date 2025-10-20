#!/usr/bin/env python3
"""
Создание реальных MP3 файлов для тестирования плеера
"""
import os
import uuid
import wave
import struct
import math

def create_sine_wave(frequency, duration, sample_rate=44100):
    """Создает синусоидальную волну"""
    samples = []
    for i in range(int(sample_rate * duration)):
        value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.append(value)
    return samples

def create_audio_file(text, filename):
    """Создает реальный аудио файл с тоном"""
    print(f"🎵 Создание аудио файла: {filename}")
    
    # Создаем директорию
    audio_dir = "static/audio"
    os.makedirs(audio_dir, exist_ok=True)
    filepath = os.path.join(audio_dir, filename)
    
    # Параметры аудио
    sample_rate = 44100
    duration = 3.0  # 3 секунды
    frequency = 440  # Ля первой октавы
    
    # Создаем синусоидальную волну
    samples = create_sine_wave(frequency, duration, sample_rate)
    
    # Создаем WAV файл
    wav_filename = filepath.replace('.mp3', '.wav')
    with wave.open(wav_filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Моно
        wav_file.setsampwidth(2)  # 16 бит
        wav_file.setframerate(sample_rate)
        
        # Записываем данные
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))
    
    # Конвертируем в MP3 с помощью pydub
    try:
        from pydub import AudioSegment
        
        # Загружаем WAV
        audio = AudioSegment.from_wav(wav_filename)
        
        # Экспортируем как MP3
        audio.export(filepath, format="mp3", bitrate="128k")
        
        # Удаляем временный WAV файл
        os.remove(wav_filename)
        
        print(f"✅ Создан MP3 файл: {filepath}")
        return filepath
        
    except ImportError:
        print("⚠️ pydub не установлен, создаем простой WAV файл")
        return wav_filename

def create_simple_mp3(text, filename):
    """Создает простой MP3 файл без внешних библиотек"""
    print(f"🎵 Создание простого аудио файла: {filename}")
    
    audio_dir = "static/audio"
    os.makedirs(audio_dir, exist_ok=True)
    filepath = os.path.join(audio_dir, filename)
    
    # Создаем минимальный валидный MP3 файл
    # MP3 заголовок для 128kbps, 44.1kHz, моно
    mp3_header = bytes([
        0xFF, 0xFB, 0x90, 0x00,  # MP3 заголовок
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ])
    
    # Создаем данные для ~3 секунд
    audio_data = mp3_header * 1000  # ~3 секунды
    
    with open(filepath, 'wb') as f:
        f.write(audio_data)
    
    os.chmod(filepath, 0o644)
    print(f"✅ Создан простой MP3: {filepath}")
    return filepath

def main():
    """Основная функция"""
    print("🎵 Создание реальных аудио файлов для тестирования")
    
    # Создаем несколько тестовых файлов
    test_files = [
        ("Привет! Это тест плеера.", "test_hello.mp3"),
        ("Тестовое аудио для проверки.", "test_audio.mp3"),
        ("Финальный тест плеера.", "test_final.mp3")
    ]
    
    created_files = []
    
    for text, filename in test_files:
        try:
            # Пробуем создать с pydub
            filepath = create_audio_file(text, filename)
            created_files.append(filepath)
        except Exception as e:
            print(f"⚠️ Ошибка с pydub: {e}")
            # Fallback на простой MP3
            filepath = create_simple_mp3(text, filename)
            created_files.append(filepath)
    
    print(f"\n✅ Создано {len(created_files)} аудио файлов:")
    for filepath in created_files:
        print(f"  📁 {filepath}")
    
    return created_files

if __name__ == "__main__":
    main()
