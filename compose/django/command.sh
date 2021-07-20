#!/bin/bash -e

CYAN='\e[36m'
GREEN='\e[32m'
END='\e[0m'

# Environment variables
echo -e "${CYAN}Adding environment variables...${END}"
declare -A ENVVARS=( [DB_NAME]=${POSTGRES_DB} [DB_USER]=${POSTGRES_USER} [DB_PASSWORD]=${POSTGRES_PASSWORD} [DB_HOST]=postgres )
for K in "${!ENVVARS[@]}"; do echo export $K="${ENVVARS[$K]}" >> ${HOME}/.bashrc && echo -e "${CYAN}Added $K${END}"; done
echo -e "${CYAN}Reloading environment variables...${END}"
source ${HOME}/.bashrc && echo -e "${GREEN}Done!${END}"

# Run migrations
echo -e "${CYAN}Updating database...${END}"
python manage.py migrate && echo -e "${GREEN}Done!${END}"

# Statics
if [ ! -d "${STATIC_ROOT}" ]; then
    echo -e "${CYAN}Collecting statics...${END}"
    python manage.py collectstatic --noinput && echo -e "${GREEN}Done!${END}"
else
    echo -e "${GREEN}Static files already exists!${END}"
fi

# Start server
echo -e "${CYAN}Starting server...${END}"
gunicorn --config python:oilandrope.gunicorn_conf && echo -e "${GREEN}Done!${END}"

# Waiting for logfiles to be created
sleep 2
# Reading logfiles
echo -e "${CYAN}Attaching to log files...${END}"
tail -f -n 30 ${GUNICORN_ACCESS_LOGFILE} ${GUNICORN_ERROR_LOGFILE}