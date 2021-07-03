#!/bin/bash -e

CYAN='\e[36m'
GREEN='\e[32m'
END='\e[0m'

# Environment variables
echo -e "${CYAN}Adding environment variables...${END}"
declare -A ENVVARS=( [DB_NAME]=${POSTGRES_DB} [DB_USER]=${POSTGRES_USER} [DB_PASSWORD]=${POSTGRES_PASSWORD} )
for K in "${!ENVVARS[@]}"; do export $K="${ENVVARS[$K]}" && echo -e "${CYAN}Added $K${END}"; done

# Run migrations
echo -e "${CYAN}Updating database...${END}"
python manage.py migrate && echo -e "${GREEN}Done!${END}"

# Statics
echo -e "${CYAN}Collecting statics...${END}"
python manage.py collectstatic --noinput && echo -e "${GREEN}Done!${END}"

# Start server
echo -e "${CYAN}Starting server...${END}"
gunicorn "${GUNICORN_WSGI_MODULE}":application \
--access-logfile - --error-logfile - \
--bind 0.0.0.0:8000 \
--reload --workers 1
