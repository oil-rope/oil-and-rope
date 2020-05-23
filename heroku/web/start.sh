#!/usr/bin/env bash

CYAN='\e[36m'
GREEN='\e[32m'
END='\e[0m'

# Run migrations
echo -e "${CYAN}Updating database...${END}"
python manage.py migrate && echo -e "${GREEN}Done!${END}"

# Statics
echo -e "${CYAN}Collecting statics...${END}"
python manage.py collectstatic --noinput && echo -e "${GREEN}Done!${END}"

# Checking for existing socket
if test -f "${GUNICORN_SOCK}"; then
  echo -e "${CYAN}Socket exists, deleting...${END}"
  rm -f ${GUNICORN_SOCK} && echo "${GREEN}Done!${END}"
else
  echo -e "${CYAN}Socket file doesn't exist.${END}"
fi

# Start server
echo -e "${CYAN}Starting server...${END}"
gunicorn ${GUNICORN_WSGI_MODULE}:application -c python:${GUNICORN_CONFIG_FILE} && echo -e "${GREEN}Done!${END}"

# Listening to log
tail -f -n 5 ${GUNICORN_ACCESS_LOGFILE}