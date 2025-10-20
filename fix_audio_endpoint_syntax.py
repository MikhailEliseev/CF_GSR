#!/usr/bin/env python3
"""
Исправление синтаксической ошибки в audio endpoint
"""

import paramiko
import time

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def fix_audio_endpoint_syntax():
    """Исправляем синтаксическую ошибку в audio endpoint"""
    print("🔧 Исправляем синтаксическую ошибку...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Восстанавливаем из бекапа
        print("\n1️⃣ Восстанавливаем из бекапа...")
        stdin, stdout, stderr = ssh.exec_command("cp /root/routes/vacancies.py.backup_audio /root/routes/vacancies.py")
        stdout.read()
        print("✅ Восстановлено из бекапа")
        
        # 2. Добавляем правильный endpoint
        print("\n2️⃣ Добавляем правильный endpoint...")
        
        correct_audio_endpoint = '''

@vacancies_bp.route('/api/vacancies/generate-audio', methods=['POST'])
def generate_audio():
    """Генерация аудио через ElevenLabs (как в модуле трендвочинга)"""
    try:
        data = request.get_json() or {}
        text = (data.get("text") or "").strip()
        
        if not text:
            return jsonify({"success": False, "message": "Текст для озвучки не передан"}), 400
        
        # Получаем настройки модуля
        settings = Settings.query.filter_by(module_name='vacancies').first()
        if not settings:
            return jsonify({"success": False, "message": "Настройки модуля не найдены"}), 400
        
        additional = settings.get_additional_settings() or {}
        
        # Настройки голоса (как в трендвочинге)
        voice_id = data.get("voice_id") or additional.get("default_voice_id") or "jP9L6ZC55cz5mmx4ZpCk"
        model_id = data.get("model_id") or additional.get("default_voice_model") or "eleven_flash_v2_5"
        stability = float(data.get("stability", 0.5))
        similarity_boost = float(data.get("similarity_boost", 0.5))
        
        # Получаем API ключ
        api_keys = settings.get_api_keys() or {}
        elevenlabs_key = api_keys.get('elevenlabs_api_key')
        
        if not elevenlabs_key:
            return jsonify({
                "success": False, 
                "message": "ElevenLabs API ключ не настроен"
            }), 400
        
        # Используем ElevenLabs API
        try:
            from api.elevenlabs_simple import ElevenLabsSimple
            client = ElevenLabsSimple(elevenlabs_key)
            
            # Генерируем аудио
            audio_url = client.generate_audio(
                text, 
                voice_id=voice_id, 
                model_id=model_id
            )
            
            if audio_url:
                return jsonify({
                    "success": True,
                    "audio_url": audio_url,
                    "voice_id": voice_id,
                    "model_id": model_id
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Ошибка генерации аудио через ElevenLabs"
                }), 500
                
        except Exception as e:
            logger.error(f"Ошибка ElevenLabs: {e}")
            return jsonify({
                "success": False,
                "message": f"Ошибка ElevenLabs API: {str(e)}"
            }), 500
            
    except Exception as e:
        logger.error(f"Ошибка генерации аудио: {e}")
        return jsonify({
            "success": False,
            "message": f"Ошибка: {str(e)}"
        }), 500
'''
        
        # Добавляем правильный endpoint
        stdin, stdout, stderr = ssh.exec_command("echo '" + correct_audio_endpoint + "' >> /root/routes/vacancies.py")
        stdout.read()
        print("✅ Правильный endpoint добавлен")
        
        # 3. Проверяем синтаксис
        print("\n3️⃣ Проверяем синтаксис...")
        stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile /root/routes/vacancies.py")
        compile_errors = stderr.read().decode()
        
        if compile_errors:
            print("❌ Ошибки компиляции:")
            print(compile_errors)
            return False
        else:
            print("✅ Синтаксис корректен")
        
        # 4. Перезапускаем сервер
        print("\n4️⃣ Перезапускаем сервер...")
        ssh.exec_command("pkill -f python.*app")
        time.sleep(3)
        ssh.exec_command("cd /root && nohup python3 app.py > server.log 2>&1 &")
        time.sleep(5)
        
        # 5. Проверяем что сервер запустился
        print("\n5️⃣ Проверяем сервер...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep python.*app | grep -v grep")
        processes = stdout.read().decode()
        if processes:
            print("✅ Сервер запущен")
        else:
            print("❌ Сервер не запустился")
            return False
        
        # 6. Тестируем endpoint
        print("\n6️⃣ Тестируем endpoint...")
        test_payload = {
            "text": "Привет! Это тест генерации аудио."
        }
        
        import json
        test_cmd = f"curl -X POST -H 'Content-Type: application/json' -d '{json.dumps(test_payload)}' http://localhost:5000/api/vacancies/generate-audio"
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        result = stdout.read().decode()
        
        if "success" in result:
            print("✅ Endpoint работает!")
            print("🎉 Проблема решена!")
            return True
        else:
            print(f"❌ Endpoint не работает: {result[:200]}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    success = fix_audio_endpoint_syntax()
    if success:
        print("\n✅ Endpoint для генерации аудио работает!")
        print("Теперь можно тестировать на http://72.56.66.228/module/vacancies")
    else:
        print("\n❌ Проблема не решена")
