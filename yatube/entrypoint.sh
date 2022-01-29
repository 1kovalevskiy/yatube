#!/bin/bash
python manage.py collectstatic --noinput &&
python manage.py migrate --noinput &&
python manage.py loaddata dump.json &&
gunicorn yatube.wsgi:application --bind 0.0.0.0:8000