#!/usr/bin/env bash

/usr/local/bin/confd -onetime -backend env

python3 manage.py collectstatic
python3 manage.py migrate
python3 manage.py create-superuser --preserve --username $DJANGO_SUPERUSER --password $DJANGO_SUPERPASS --email $DJANGO_EMAIL

# Fix Permissions prior to running uwsgi server
chown -R www-data:www-data /static
chown -R www-data:www-data /nsupdate

uwsgi --uid=www-data --gid=www-data --ini uwsgi.ini
