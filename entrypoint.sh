python tables.py migrate
celery -A tasks worker --detach -f stdout --loglevel DEBUG
python main.py