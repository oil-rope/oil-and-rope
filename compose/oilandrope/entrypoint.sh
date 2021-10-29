#!/bin/bash

poetry run gunicorn --bind=0.0.0.0:8000 --workers=4 --reload --log-level=DEBUG oilandrope.wsgi
