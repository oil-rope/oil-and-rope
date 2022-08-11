#!/usr/bin/env bash

set -Ee

END='\033[0m'
ERROR='\033[0;31m'
SUCCESS='\033[0;32m'
INFO='\033[0;36m'

echo -e "${INFO}Checking project...${END}"
poetry run ./manage.py check && echo -e "${GREEN}Project okay!${END}" || exit 1

echo -e "${INFO}Running migrations...${END}"
poetry run ./manage.py migrate && echo -e "${GREEN}Database up to date!${END}" || exit 1

echo -e "${INFO}Starting project...${END}"
poetry run gunicorn --config=python:oilandrope.gunicorn_conf
