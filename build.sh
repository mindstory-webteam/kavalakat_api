#!/usr/bin/env bash

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Running migrations..."
python manage.py migrate

echo "👤 Creating superuser if not exists..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@gmail.com", "admin123")
    print("Superuser created")
else:
    print("Superuser already exists")
END

echo "🚀 Starting server..."
gunicorn kavalakat.wsgi:application