#!/bin/sh

parentdir=$(dirname `pwd`)
django_folder="$parentdir/oilandrope"
bot_executable="$django_folder/run.py"
django_executable="$django_folder/manage.py"
database_prefix="--database="
database="default"

# Run Bot
python3 $bot_executable

# Checking if database has been provided
if [ -z $1 ] || [ $# -eq 0 ]; then
    echo Using default database.
else
    if [[ $1 == $database_prefix* ]]; then
        echo Using $1.
        database=${1#"$database_prefix"}
    else
        echo Database invalid, using default.
    fi
fi

# Run Django
python3 $django_executable runserver_plus 0.0.0.0:8000
