# Local Trendwatching Test Checklist

1. **Environment**
   - `python -m venv venv && source venv/bin/activate`
   - `pip install -r requirements.txt`
   - Create `.env` with `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, and API keys or leave blanks for fallback mode.
2. **Database**
   - Run `python scripts/bootstrap_trends_environment.py` to create tables and seed demo competitors/settings.
3. **Services**
   - Start Redis (`redis-server` or Docker) and Celery `celery -A celery_app.celery_app worker --loglevel=info`.
4. **Application**
   - Launch Flask via `python app.py` and open `http://localhost:5000/module/trends`.
5. **Pipeline Walkthrough**
   - Step 1: Collect demo reels (Apify fallback returns sample data instantly).
   - Step 2: Select a reel from the table.
   - Step 3: Transcribe (AssemblyAI service returns demo transcript without keys).
   - Step 4: Rewrite text (OpenAI service fallback produces rewritten copy).
   - Step 5: Generate audio (ElevenLabs fallback returns demo mp3).
   - Step 6: Generate video (HeyGen fallback returns demo mp4).
6. **Real APIs**
   - Populate `.env` with live keys and re-run steps to gauge latency; note Apify may take 30–60s per request.
   - If 504 occurs, capture timings for future Celery/background refactor.
