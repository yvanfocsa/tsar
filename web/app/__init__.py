# web/app/__init__.py
from __future__ import annotations

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

from .config import Config

db = SQLAlchemy()

# On ajoute un paramètre pour les context processors
def create_app(register_blueprints=True, register_context_processors=True) -> Flask:
    """Factory principale : instancie Flask, BD, OAuth, modules, routes."""
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)

    # 1️⃣ DB
    db.init_app(app)
    with app.app_context():
        from . import models
        db.create_all()

    # 2️⃣ Auth0
    oauth = OAuth(app)
    oauth.register(
        name="auth0",
        client_id=app.config["AUTH0_CLIENT_ID"],
        client_secret=app.config["AUTH0_CLIENT_SECRET"],
        client_kwargs={"scope": "openid profile email"},
        server_metadata_url=(
            f'https://{app.config["AUTH0_DOMAIN"]}'
            '/.well-known/openid-configuration'
        ),
    )
    app.oauth = oauth

    # 3️⃣ Modules dynamiques
    from .modules import load_modules
    load_modules()

    # 4️⃣ Routes & login (CONDITIONNEL)
    if register_blueprints:
        from .routes import login_manager, bp as routes_bp
        login_manager.login_view = "routes.login"
        login_manager.init_app(app)
        app.register_blueprint(routes_bp)

    # 5️⃣ Celery
    from .tasks import celery as celery_app
    celery_app.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
    )
    app.celery = celery_app

    # 6️⃣ Context Processor (CONDITIONNEL)
    if register_context_processors:
        @app.context_processor
        def inject_user_info():
            from flask import session
            from flask_login import current_user
            from .models import UserProfile

            if not current_user.is_authenticated:
                return dict(display_name="Utilisateur", email=None)

            profile = UserProfile.query.filter_by(user_sub=current_user.sub).first()
            user_data = session.get("user", {})
            email = user_data.get("email")

            if profile and profile.display_name:
                display_name = profile.display_name
            else:
                auth0_name = user_data.get("nickname") or user_data.get("name")
                if auth0_name and "@" not in auth0_name:
                    display_name = auth0_name
                elif email:
                    display_name = email.split('@')[0]
                else:
                    display_name = "Utilisateur"
            
            return dict(display_name=display_name, email=email)

    return app
