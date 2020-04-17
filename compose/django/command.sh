#!/bin/sh

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
/usr/local/bin/gunicorn oilandrope.wsgi:application --bind 0.0.0.0:5000 --workers 4 --access-logfile -
