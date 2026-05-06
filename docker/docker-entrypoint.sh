#!/bin/bash

# Collect static files
#echo "Collect static files"
#python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python3 /nsupdate/manage.py migrate
python3 /nsupdate/manage.py createsuperuser --noinput

# Start server
echo "Starting server"
#python3 /nsupdate/manage.py runserver 0.0.0.0:8000
cd /nsupdate/src
#gunicorn --workers=4 --log-level=info --forwarded-allow-ips="$TRUSTED_PROXIES" --bind 0.0.0.0:8000 nsupdate.wsgi
gunicorn --workers=4 --log-level=info --forwarded-allow-ips='*' --bind 0.0.0.0:8000 nsupdate.wsgi
