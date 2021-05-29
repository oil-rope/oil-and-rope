#!/bin/bash

CYAN='\e[36m'
GREEN='\e[32m'
END='\e[0m'

# Start server
echo -e "${CYAN}Starting Daphne...${END}"
daphne "${DAPHNE_ASGI_MODULE}":application -b 0.0.0.0 -p 8001 --access-log -