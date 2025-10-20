# Trends Pipeline Service Behavior

| Stage        | Service wrapper                        | Without API key | With API key |
|--------------|-----------------------------------------|-----------------|--------------|
| Transcribe   | `services/assembly_service.py`          | Returns demo transcript (informational text) | Uses AssemblyAI via `AssemblyAIClient` |
| Rewrite      | `services/openai_service.py`            | Produces demo rewrite mentioning trends      | Uses OpenAI Assistant (`generate_text_for_video` & chat rewrite) |
| Audio        | `services/elevenlabs_service.py`        | Returns hosted demo mp3 (`_DEMO_AUDIO`)      | Streams ElevenLabs audio via `generate_audio` |
| Video        | `services/heygen_service.py`            | Returns hosted demo mp4 (`_DEMO_VIDEO`)      | Launches HeyGen job and resolves video / video_id |

## Manual Test Checklist
1. Collect reels (demo or live) and select a post.
2. `/api/trends/transcribe` ⇒ verify JSON includes `transcript` and no error key.
3. `/api/trends/rewrite` ⇒ verify `rewritten_text` present and fallback message clearly marked.
4. `/api/trends/generate-audio` ⇒ check `audio_url`; when fallback used, response includes `warning` field.
5. `/api/trends/generate-video` ⇒ check `video_url` or `video_id` and `warning` value if demo mode.

> When switching to live keys, remove the warnings automatically (they are only included when no key was configured) and monitor runtime/quotas as noted in `REAL_API_READY.md`.
