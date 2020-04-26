#!/usr/bin/env bash

CYAN='\e[36m'
GREEN='\e[32m'
END='\e[0m'

# Statics
echo -e "${CYAN}Collecting statics...${END}"
python manage.py collectstatic --noinput && echo -e "${GREEN}Done!${END}"

# Run migrations
echo -e "${CYAN}Running migrations...${END}"
python manage.py migrate && echo -e "${GREEN}Done!${END}"

# Start server
echo -e "${CYAN}Starting gunicorn...${END}"
gunicorn oilandrope.wsgi:application --workers 4 --access-logfile -
