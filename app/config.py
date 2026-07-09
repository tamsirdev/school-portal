import os


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://school:school@localhost:5432/school"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL",
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    )
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
