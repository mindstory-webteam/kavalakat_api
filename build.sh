#!/usr/bin/env bash
set -o errexit

echo "========================================="
echo "=== Step 1: Installing dependencies  ==="
echo "========================================="
pip install -r requirements.txt

echo "========================================="
echo "=== Step 2: Collecting static files  ==="
echo "========================================="
python manage.py collectstatic --no-input

echo "========================================="
echo "=== Step 3: Running migrations        ==="
echo "========================================="
python manage.py migrate --run-syncdb

echo "========================================="
echo "=== Step 4: Creating superuser        ==="
echo "========================================="
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@kavalakat.com', 'Admin@1234')
    print('SUCCESS: Superuser created — username: admin / password: Admin@1234')
else:
    print('INFO: Superuser already exists')
PYEOF

echo "========================================="
echo "=== Step 5: Seeding portfolio data    ==="
echo "========================================="
python manage.py seed_portfolio || echo "Portfolio already seeded or seed command not found"

echo "========================================="
echo "=== BUILD COMPLETE — Server starting  ==="
echo "========================================="