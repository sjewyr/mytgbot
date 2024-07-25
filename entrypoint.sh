python tables.py migrate
celery -A celery_tasks worker --detach -f stdout --loglevel DEBUG
python main.py
