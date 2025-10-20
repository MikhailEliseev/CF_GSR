#!/usr/bin/env python3
"""
Исправление синтаксической ошибки в routes/vacancies.py
"""

import paramiko

SERVER_HOST = "72.56.66.228"
SERVER_USER = "root"
SERVER_PASSWORD = "g2D,RytdQoSAYv"

def fix_syntax_error():
    """Исправляем синтаксическую ошибку"""
    print("🔧 Исправляем синтаксическую ошибку...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
    
    try:
        # 1. Создаем бекап
        print("\n1️⃣ Создаем бекап...")
        stdin, stdout, stderr = ssh.exec_command("cp /root/routes/vacancies.py /root/routes/vacancies.py.backup_$(date +%Y%m%d_%H%M%S)")
        stdout.read()
        print("✅ Бекап создан")
        
        # 2. Исправляем синтаксическую ошибку
        print("\n2️⃣ Исправляем синтаксическую ошибку...")
        
        # Удаляем неправильную строку
        fix_cmd = '''
# Удаляем строку с ошибкой
sed -i '/@vacancies_bp.route(\/api\/vacancies\/generate-audio-fallback, methods=\[POST\])/d' /root/routes/vacancies.py

# Добавляем правильную строку
cat >> /root/routes/vacancies.py << 'EOF'

@vacancies_bp.route('/api/vacancies/generate-audio-fallback', methods=['POST'])
def generate_audio_fallback():
    """Fallback генерация аудио через espeak"""
    try:
        from services.elevenlabs_fallback import ElevenLabsFallback
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"success": False, "error": "Текст не указан"}), 400
        
        print(f"Генерируем fallback аудио для текста: {text[:50]}...")
        
        # Используем fallback
        fallback = ElevenLabsFallback()
        audio_base64 = fallback.generate_audio(text)
        
        if audio_base64:
            return jsonify({
                "success": True,
                "audio_data": audio_base64,
                "method": "espeak_fallback",
                "message": "Аудио сгенерировано через системный TTS"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ошибка генерации fallback аудио"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Ошибка fallback: {str(e)}"
        }), 500
EOF
'''
        
        stdin, stdout, stderr = ssh.exec_command(fix_cmd)
        stdout.read()
        stderr.read()
        print("✅ Синтаксическая ошибка исправлена")
        
        # 3. Проверяем синтаксис
        print("\n3️⃣ Проверяем синтаксис...")
        stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile /root/routes/vacancies.py")
        compile_result = stdout.read().decode()
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
            
            # Проверяем логи
            stdin, stdout, stderr = ssh.exec_command("tail -10 /root/server.log")
            error_logs = stdout.read().decode()
            print("Логи ошибок:")
            print(error_logs)
            return False
        
        # 6. Тестируем доступность
        print("\n6️⃣ Тестируем доступность...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000/")
        curl_result = stdout.read().decode()
        if "html" in curl_result.lower():
            print("✅ Сервер отвечает")
        else:
            print("❌ Сервер не отвечает")
            return False
        
        # 7. Тестируем fallback endpoint
        print("\n7️⃣ Тестируем fallback endpoint...")
        test_payload = {
            "text": "Привет! Это тест fallback аудио."
        }
        
        import json
        test_cmd = f"curl -X POST -H 'Content-Type: application/json' -d '{json.dumps(test_payload)}' http://localhost:5000/api/vacancies/generate-audio-fallback"
        stdin, stdout, stderr = ssh.exec_command(test_cmd)
        result = stdout.read().decode()
        
        if "success" in result and "audio_data" in result:
            print("✅ Fallback endpoint работает!")
            print("🎉 Проблема решена!")
            return True
        else:
            print(f"❌ Fallback не работает: {result[:200]}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    success = fix_syntax_error()
    if success:
        print("\n✅ ElevenLabs fallback готов к использованию!")
        print("Теперь можно тестировать на http://72.56.66.228/module/vacancies")
    else:
        print("\n❌ Проблема не решена")
