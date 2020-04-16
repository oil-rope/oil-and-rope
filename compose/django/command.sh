#!/bin/bash

# Compile JavaScript
echo 'Intalling NPM dependencies and building...'
npm install && npm run build echo 'Done!'

# Run migrations
echo 'Updating database...'
python manage.py migrate && echo 'Done!'

# Start server
echo 'Starting server...'
gunicorn oilandrope.wsgi --chdir=/app -w 4
