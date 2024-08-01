
rm -f './celerybeat.pid'
celery -A celery_tasks beat -l info
