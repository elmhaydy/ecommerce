#!/usr/bin/env bash
set -o errexit

echo "==> Running database migrations..."
python manage.py migrate --no-input

echo "==> Checking and seeding database with initial data..."
python manage.py seed_db --auto

echo "==> Starting Gunicorn application server..."
exec gunicorn config.wsgi:application

