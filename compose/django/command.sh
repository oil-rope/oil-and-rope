#!/bin/bash

# Compile JavaScript
echo 'Intalling NPM dependencies and building...'
npm install && npm run build echo 'Done!'

# Run migrations
echo 'Updating database...'
python manage.py migrate && echo 'Done!'

# Statics
echo 'Collecting statics...'
python manage.py collectstatic --noinput

# Start server
echo 'Starting server...'
/usr/local/bin/gunicorn oilandrope.wsgi --bind 0.0.0.0:80 --workers 4 --access-logfile -
