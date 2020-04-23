#! /bin/sh

# Start server
echo 'Starting Daphne...'
/usr/local/bin/daphne oilandrope.asgi:application -b 0.0.0.0 -p 5001
