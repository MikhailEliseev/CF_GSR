"""Flask application factory for Content Factory."""
from __future__ import annotations

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from models import db, Settings, Competitors
from config import Config
from typing import Optional, Dict, Any

socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')


def _is_missing(value: Optional[str]) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip().lower() in {'', 'none', 'null'}:
        return True
    return False


def _ensure_default_settings():
    modules = ['trends', 'vacancies', 'experts']
    default_api_keys = Config.DEFAULT_API_KEYS

    for module_name in modules:
        existing = Settings.query.filter_by(module_name=module_name).first()
        if not existing:
            settings = Settings(
                module_name=module_name,
                master_prompt="",
                api_keys="{}",
                additional_settings="{}"
            )
            sanitized_defaults = {
                key: value for key, value in default_api_keys.items() if not _is_missing(value)
            }
            settings.set_api_keys(sanitized_defaults)
            db.session.add(settings)
    db.session.commit()

    for module_name in modules:
        settings = Settings.query.filter_by(module_name=module_name).first()
        if not settings:
            continue
        api_keys = settings.get_api_keys()
        updated = False
        for key, value in default_api_keys.items():
            if _is_missing(api_keys.get(key)) and not _is_missing(value):
                api_keys[key] = value
                updated = True
        if updated:
            settings.set_api_keys(api_keys)
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)
    socketio.init_app(app)

    with app.app_context():
        db.create_all()
        _ensure_default_settings()

    from routes.trends import trends_bp
    app.register_blueprint(trends_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/module/<module_name>')
    def module_page(module_name):
        if module_name not in ['trends', 'vacancies', 'experts']:
            flash('Модуль не найден', 'error')
            return redirect(url_for('index'))
        settings = Settings.query.filter_by(module_name=module_name).first()
        return render_template(f'module_{module_name}.html', settings=settings)

    @app.route('/settings/<module_name>')
    def settings_page(module_name):
        if module_name not in ['trends', 'vacancies', 'experts']:
            flash('Модуль не найден', 'error')
            return redirect(url_for('index'))

        settings = Settings.query.filter_by(module_name=module_name).first()
        competitors = []
        if module_name == 'trends':
            competitors = Competitors.query.filter_by(is_active=True).all()

        return render_template(
            'settings.html',
            module_name=module_name,
            settings=settings,
            competitors=competitors
        )

    @app.route('/api/settings/<module_name>', methods=['GET', 'POST'])
    def manage_settings(module_name):
        try:
            settings = Settings.query.filter_by(module_name=module_name).first()

            if request.method == 'GET':
                if not settings:
                    return jsonify({
                        'success': True,
                        'api_keys': {},
                        'openai_assistant_id': '',
                        'master_prompt': '',
                        'additional_settings': {}
                    })

                return jsonify({
                    'success': True,
                    'api_keys': settings.get_api_keys(),
                    'openai_assistant_id': settings.openai_assistant_id or '',
                    'master_prompt': settings.master_prompt or '',
                    'additional_settings': settings.get_additional_settings()
                })

            def _clean(value: Optional[str]) -> Optional[str]:
                if value is None:
                    return None
                stripped = value.strip()
                if not stripped:
                    return None
                if stripped.lower() in {'none', 'null'}:
                    return None
                return stripped

            def _parse_form_payload(form_data: Dict[str, Any]) -> Dict[str, Any]:
                payload: Dict[str, Any] = {
                    'openai_assistant_id': _clean(form_data.get('openai_assistant_id')),
                    'master_prompt': form_data.get('master_prompt'),
                    'api_keys': {
                        'openai_api_key': _clean(form_data.get('openai_api_key')),
                        'elevenlabs_api_key': _clean(form_data.get('elevenlabs_api_key')),
                        'heygen_api_key': _clean(form_data.get('heygen_api_key')),
                        'apify_api_key': _clean(form_data.get('apify_api_key')),
                        'assemblyai_api_key': _clean(form_data.get('assemblyai_api_key'))
                    },
                    'additional_settings': {
                        'default_voice_id': _clean(form_data.get('default_voice_id')),
                        'default_avatar_id': _clean(form_data.get('default_avatar_id'))
                    }
                }

                if module_name == 'vacancies':
                    payload['additional_settings']['google_sheets_url'] = _clean(form_data.get('google_sheets_url'))
                if module_name == 'experts':
                    payload['additional_settings']['consumer_profile'] = form_data.get('consumer_profile', '')

                payload['additional_settings'] = {
                    key: value for key, value in payload['additional_settings'].items() if value is not None
                }
                return payload

            data = request.get_json(silent=True)
            if data is None:
                if request.form:
                    data = _parse_form_payload(request.form.to_dict())
                else:
                    data = {}

            if not settings:
                settings = Settings(module_name=module_name)
                db.session.add(settings)

            settings.openai_assistant_id = data.get('openai_assistant_id', settings.openai_assistant_id)
            settings.master_prompt = data.get('master_prompt', settings.master_prompt)

            if 'api_keys' in data and isinstance(data['api_keys'], dict):
                existing_keys = settings.get_api_keys()
                for key_name, value in data['api_keys'].items():
                    cleaned = _clean(value)
                    if cleaned:
                        existing_keys[key_name] = cleaned
                settings.set_api_keys(existing_keys)
            else:
                api_keys = settings.get_api_keys()
                for key_name in ['openai_api_key', 'elevenlabs_api_key', 'heygen_api_key', 'apify_api_key', 'assemblyai_api_key']:
                    if key_name in data:
                        cleaned = _clean(data[key_name])
                        if cleaned:
                            api_keys[key_name] = cleaned
                settings.set_api_keys(api_keys)

            if 'additional_settings' in data and isinstance(data['additional_settings'], dict):
                additional = settings.get_additional_settings()
                for key_name, value in data['additional_settings'].items():
                    cleaned = _clean(value) if isinstance(value, str) else value
                    if cleaned is not None:
                        additional[key_name] = cleaned
                settings.set_additional_settings(additional)

            db.session.commit()
            return jsonify({'success': True, 'message': 'Настройки сохранены'})
        except Exception as exc:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(exc)}), 500

    return app, socketio


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('join_task')
def handle_join_task(data):
    task_id = data['task_id']
    from flask_socketio import join_room
    join_room(task_id)

