#!/usr/bin/env bash

CYAN='\e[36m'
END='\e[0m'

# Start server
echo -e "${CYAN}Starting Daphne...${END}"
daphne ${DAPHNE_ASGI_MODULE}:application -u ${DAPHNE_SOCKET} -p ${DAPHNE_PORT}
