FROM python

ENV POETRY_VERSION=1.8.3 \
POETRY_VIRTUALENVS_CREATE=false \
POETRY_CACHE_DIR='/var/cache/pypoetry' \
POETRY_HOME='/usr/local' \ 
#TELEGRAM_BOT
TELEGRAMBOT_DB_HOST=postgres_service \
TELEGRAMBOT_DB_PORT=5432 \
TELEGRAMBOT_DB_NAME=telegrambot \
TELEGRAMBOT_DB_USER=postgres \
TELEGRAMBOT_DB_PASSWORD=postgres 
COPY . .

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN poetry install --no-interaction --no-cache --no-root

ENTRYPOINT ["bash", "entrypoint.sh"]