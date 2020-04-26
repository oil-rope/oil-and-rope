#!/usr/bin/env bash

CYAN='\e[36m'
GREEN='\e[32m'
END='\e[0m'

set -e
cmd="$*"

wait_for_postgres() {
python << END
import sys

import psycopg2

try:
    psycopg2.connect(
        dbname="${DB_NAME}",
        user="${DB_USER}",
        password="${DB_PASSWORD}",
        host="${DB_HOST}",
        port="${DB_PORT}"
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}

until wait_for_postgres; do
    >&2 echo -e "${CYAN}Waiting for Postgres...${END}"
    sleep 1
done
>&2 echo -e "${GREEN}Postgres is available!${END}"

exec "$cmd"