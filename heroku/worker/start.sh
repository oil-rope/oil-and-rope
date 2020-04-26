#!/usr/bin/env bash

CYAN='\e[36m'
GREEN='\e[32m'
END='\e[0m'

# Run migrations
echo -e "${CYAN}Running migrations...${END}"
python manage.py migrate && echo -e "${GREEN}Done!${END}"

echo -e "${CYAN}Starting bot...${END}"
python manage.py runbot