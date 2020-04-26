#!/usr/bin/env bash

# Start server
echo 'Starting Daphne...'
daphne oilandrope.asgi:application -b 0.0.0.0 -p 5001
