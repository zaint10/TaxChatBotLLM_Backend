#!/bin/bash
SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"zat938@gmail.com"}

# Activate the virtual environment
. /opt/venv/bin/

python manage.py migrate
python manage.py createsuperuser --email $SUPERUSER_EMAIL --noinput || true