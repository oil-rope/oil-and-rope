#!/usr/bin/env bash

set -Ee

END='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'

echo -e "${CYAN}Checking project...${END}"
poetry run ./manage.py check && echo -e "${GREEN}Project okay!${END}" || \
echo -e "${RED}Project is not okay${END}"

echo -e "${CYAN}Running migrations...${END}"
poetry run ./manage.py migrate && echo -e "${GREEN}Database up to date!${END}" || \
echo -e "${RED}Couldn't update database. Can the project access?${END}"

echo -e "${CYAN}Starting project...${END}"
poetry run gunicorn --config=python:oilandrope.gunicorn_conf
