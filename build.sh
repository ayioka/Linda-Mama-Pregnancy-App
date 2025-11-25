#!/usr/bin/env bash
# build.sh

echo "Starting build process..."

# Install dependencies
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py migrate
python manage.py migrate account
python manage.py migrate pregnancy

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
