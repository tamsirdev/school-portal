#!/bin/sh
set -e

case "${SERVICE_TYPE:-web}" in
  web)
    flask db upgrade
    exec gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - manage:app
    ;;
  worker)
    exec celery -A app.services.celery_app worker --loglevel=info --concurrency=2
    ;;
  beat)
    exec celery -A app.services.celery_app beat --loglevel=info
    ;;
  *)
    echo "Unknown SERVICE_TYPE: $SERVICE_TYPE"
    exit 1
    ;;
esac