#!/usr/bin/env bash

set -Ee

END='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'

echo -e "${CYAN}Checking project...${END}"
python ./manage.py check && echo -e "${GREEN}Project okay!${END}" || \
echo -e "${RED}Project is not okay${END}"

echo -e "${CYAN}Running migrations...${END}"
python ./manage.py migrate && echo -e "${GREEN}Database up to date!${END}" || \
echo -e "${RED}Couldn't update database. Can the project access?${END}"

echo -e "${CYAN}Generating translations...${END}"
python ./manage.py compilemessages --locale=es --use-fuzzy && echo -e "${GREEN}Translations generated!${END}" || \
echo -e "${RED}Couldn't generate translations${END}"

echo -e "${CYAN}Collecting static...${END}"
python ./manage.py collectstatic --no-input && echo -e "${GREEN}Static files collected!${END}" || \
echo -e "${RED}Couldn't collect static files${END}"

if [[ -v ADMIN_PASSWORD ]]; then
  echo -e "${CYAN}Creating admin user with given password...${END}"
  python ./manage.py shell -c \
  'from registration.models import User;import os;User.objects.create_superuser("admin", "admin@gmail.com", os.getenv("ADMIN_PASSWORD"))' && \
  echo -e "${GREEN}Created superuser with username 'admin'!${END}" || echo -e "${RED}Couldn't create admin user${END}"
fi

echo -e "${CYAN}Starting project...${END}"
python -m daphne \
--bind=${GUNICORN_IP} \
--port=${GUNICORN_PORT} \
--access-log - \
--verbosity=3 \
${GUNICORN_WSGI_MODULE}:application
