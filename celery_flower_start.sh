celery -A celery_tasks  \
    --broker="${TELEGRAMBOT_BROKER}" \
    flower
