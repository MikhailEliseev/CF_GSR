"""Utility script to bootstrap local DB state for the trends pipeline."""
from __future__ import annotations

import json
from pathlib import Path

from app import create_app
from models import db, Settings, Competitors

DEFAULT_COMPETITORS = [
    "rem.vac",
    "msk.job",
    "rabota_navatu14",
]

DEFAULT_TRENDS_SETTINGS = {
    "master_prompt": "Создавай захватывающие сценарии для коротких обучающих видео.",
    "additional_settings": {
        "default_voice_id": "demo_voice",
        "default_avatar_id": "demo_avatar",
        "default_voice_model": "eleven_flash_v2_5",
    },
}


def ensure_settings(module: str, overrides: dict | None = None) -> None:
    """Ensure Settings row exists for module with sensible defaults."""
    overrides = overrides or {}
    record = Settings.query.filter_by(module_name=module).first()
    if not record:
        record = Settings(module_name=module)
        db.session.add(record)

    if DEFAULT_TRENDS_SETTINGS["master_prompt"] and not record.master_prompt:
        record.master_prompt = DEFAULT_TRENDS_SETTINGS["master_prompt"]

    settings_payload = record.get_additional_settings()
    settings_payload.update(DEFAULT_TRENDS_SETTINGS["additional_settings"])
    settings_payload.update(overrides.get("additional_settings", {}))
    record.set_additional_settings(settings_payload)

    # Never hardcode API keys here — leave placeholders and use .env in runtime.
    record.set_api_keys({**record.get_api_keys()})
    db.session.commit()


def seed_competitors(handles: list[str]) -> None:
    for handle in handles:
        if not handle:
            continue
        exists = Competitors.query.filter_by(username=handle).first()
        if exists:
            continue
        db.session.add(Competitors(username=handle.strip()))
    db.session.commit()


def main() -> None:
    app, _ = create_app()
    with app.app_context():
        db.create_all()
        ensure_settings("trends")
        seed_competitors(DEFAULT_COMPETITORS)
        print("✅ Trends module bootstrap complete.")


if __name__ == "__main__":
    main()
