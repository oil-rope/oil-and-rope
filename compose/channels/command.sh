#!/usr/bin/env bash

CYAN='\e[36m'
GREEN='\e[32m'
END='\e[0m'

# Checking for existing socket
if test -f "${DAPHNE_SOCKET}"; then
  echo -e "${CYAN}Socket exists, deleting...${END}"
  rm -f "${DAPHNE_SOCKET}" && echo "${GREEN}Done!${END}"
else
  echo -e "${CYAN}Socket file doesn't exist.${END}"
fi

# Start server
echo -e "${CYAN}Starting Daphne...${END}"
daphne "${DAPHNE_ASGI_MODULE}":application -u "${DAPHNE_SOCKET}" -p "${DAPHNE_PORT}" --access-log "${DAPHNE_ACCESS_LOGFILE}"