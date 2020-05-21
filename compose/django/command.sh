#!/usr/bin/env bash

CYAN="\e[36m"
GREEN="\e[32m"
END="\e[0m"

# Compile JavaScript
echo -e "${CYAN}Installing NPM dependencies and building...${END}"
npm install && npm run build && echo -e "${GREEN}Done!${END}"

# Run migrations
echo -e "${CYAN}Updating database...${END}"
python manage.py migrate && echo -e "${GREEN}Done!${END}"

# Statics
echo -e "${CYAN}Collecting statics...${END}"
python manage.py collectstatic --noinput && echo -e "${GREEN}Done!${END}"

# Start server
echo -e "${CYAN}Starting server...${END}"
gunicorn oilandrope.wsgi:application --bind 0.0.0.0:80 --workers 4 --reload --access-logfile -
