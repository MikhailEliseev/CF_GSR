#!/usr/bin/env python3
"""
Локальный прокси сервер для обхода CORS
"""
import asyncio
import aiohttp
from aiohttp import web
import json

async def proxy_audio(request):
    """Прокси для аудио файлов"""
    try:
        # Получаем URL из параметров
        audio_url = request.query.get('url')
        if not audio_url:
            return web.json_response({'error': 'URL не указан'}, status=400)
        
        print(f"🎵 Проксируем аудио: {audio_url}")
        
        # Загружаем аудио через прокси
        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Возвращаем аудио с CORS заголовками
                    return web.Response(
                        body=audio_data,
                        headers={
                            'Content-Type': 'audio/mpeg',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
                            'Cache-Control': 'public, max-age=3600'
                        }
                    )
                else:
                    return web.json_response({'error': f'Ошибка загрузки: {response.status}'}, status=response.status)
    
    except Exception as e:
        print(f"❌ Ошибка прокси: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def proxy_audio_post(request):
    """POST прокси для аудио файлов"""
    try:
        data = await request.json()
        audio_url = data.get('url')
        
        if not audio_url:
            return web.json_response({'error': 'URL не указан'}, status=400)
        
        print(f"🎵 POST проксируем аудио: {audio_url}")
        
        # Загружаем аудио через прокси
        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Возвращаем аудио с CORS заголовками
                    return web.Response(
                        body=audio_data,
                        headers={
                            'Content-Type': 'audio/mpeg',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
                            'Cache-Control': 'public, max-age=3600'
                        }
                    )
                else:
                    return web.json_response({'error': f'Ошибка загрузки: {response.status}'}, status=response.status)
    
    except Exception as e:
        print(f"❌ Ошибка POST прокси: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def init_app():
    """Инициализация приложения"""
    app = web.Application()
    
    # Добавляем CORS middleware
    async def cors_middleware(request, handler):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        return response
    
    app.middlewares.append(cors_middleware)
    
    # Маршруты
    app.router.add_get('/api/proxy-audio', proxy_audio)
    app.router.add_post('/api/proxy-audio', proxy_audio_post)
    
    return app

if __name__ == '__main__':
    print("🚀 Запускаем прокси сервер для обхода CORS...")
    app = asyncio.run(init_app())
    web.run_app(app, host='localhost', port=8083)
