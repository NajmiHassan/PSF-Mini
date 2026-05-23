#!/usr/bin/env bash
# Build script for Render — runs every deploy.
# Make sure this file is executable: chmod +x build.sh

set -o errexit  # exit on error

pip install -r requirements.txt

# Collect all static files (CSS) into staticfiles/
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py makemigrations scaffold_filler --no-input
python manage.py migrate --no-input
