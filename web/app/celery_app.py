# web/app/celery_app.py
from . import create_app

flask_app = create_app()
celery_app = flask_app.celery
