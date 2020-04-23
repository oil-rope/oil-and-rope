#!/bin/sh

set -e
cmd="$@"

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
    >&2 echo 'Waiting for PostgreSQL...'
    sleep 1
done
>&2 echo 'PostgreSQL is available!'

exec $cmd