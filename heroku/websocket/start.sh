#!/usr/bin/env bash

CYAN='\e[36m'
GREEN='\e[32m'
END='\e[0m'

# Checking for existing socket
if test -f "${DAPHNE_SOCKET}"; then
  echo -e "${CYAN}Socket exists, deleting...${END}"
  rm -f ${DAPHNE_SOCKET} && echo -e "${GREEN}Done!${END}"
else
  echo -e "${CYAN}Socket file doesn't exist. Creating...${END}"
  touch ${DAPHNE_ACCESS_LOGFILE} && echo -e "${GREEN}Done!${END}"
fi

# Start server
echo -e "${CYAN}Starting Daphne...${END}"
daphne ${DAPHNE_ASGI_MODULE}:application -u ${DAPHNE_SOCKET} -p ${DAPHNE_PORT} --access-log ${DAPHNE_ACCESS_LOGFILE}