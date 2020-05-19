#!/usr/bin/env bash

CYAN='\e[36m'
END='\e[0m'

# Start server
echo -e "${CYAN}Starting Daphne...${END}"
daphne oilandrope.asgi:application -b 0.0.0.0 -p 80
