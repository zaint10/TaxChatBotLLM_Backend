#!/bin/bash
# Activate the virtual environment
. /opt/venv/bin/activate

# Run the main command with the specified port
exec python manage.py runserver 0.0.0.0:${APP_PORT}