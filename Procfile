web: python manage.py collectstatic --noinput && gunicorn oilandrope.wsgi:application --workers 4 --access-logfile -
worker: python manage.py runbot