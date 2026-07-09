from celery.schedules import crontab

from app.services.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "run-risk-analysis-weekly": {
        "task": "app.services.tasks.run_risk_analysis",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),
        "args": (1,),
    },
}
