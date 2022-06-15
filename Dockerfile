FROM python:3.10-slim

RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y libpq-dev
RUN apt-get install -y gettext
RUN pip install poetry

WORKDIR /app/
COPY . /app/

RUN poetry install --no-dev

# In order to always have Gunicorn against 0.0.0.0:8000 we set the following environment variables
ENV GUNICORN_DAEMON="False" \
GUNICORN_ACCESS_LOGFILE="-" \
GUNICORN_ERROR_LOGFILE="-" \
GUNICORN_SOCK="" \
GUNICORN_IP="0.0.0.0" \
GUNICORN_PORT="8000" \
DJANGO_SETTINGS_MODULE="oilandrope.settings" \
DEBUG="False" \
DEBUG_TEMPLATE="False"

EXPOSE 8000
