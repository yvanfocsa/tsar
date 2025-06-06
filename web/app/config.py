import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    AUTH0_DOMAIN         = os.environ.get("AUTH0_DOMAIN", "")
    AUTH0_CLIENT_ID      = os.environ.get("AUTH0_CLIENT_ID", "")
    AUTH0_CLIENT_SECRET  = os.environ.get("AUTH0_CLIENT_SECRET", "")
    AUTH0_AUDIENCE       = os.environ.get("AUTH0_AUDIENCE", "")
    AUTH0_CALLBACK_URL   = os.environ.get("AUTH0_CALLBACK_URL", "")

    PDF_ENC_KEY = os.environ.get("PDF_ENC_KEY", "")

    POSTGRES_USER     = os.environ.get("POSTGRES_USER", "tsar")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "tsarpass")
    POSTGRES_DB       = os.environ.get("POSTGRES_DB", "tsar")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Celery / Redis
    CELERY_BROKER_URL  = os.environ.get("CELERY_BROKER_URL",  "redis://redis:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

    # Conteneur Kali headless utilisé par les modules
    TOOLBOX_CONTAINER = os.environ.get("TOOLBOX_CONTAINER", "toolbox")

