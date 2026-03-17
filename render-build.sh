#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files for production
echo "🔍 Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --no-input

# Create superuser if it doesn't exist
echo "👤 Setting up superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='mezui123@gmail.com',
        password='admin123'
    )
    print("✅ Superuser 'admin' created successfully")
else:
    print("ℹ️  Superuser 'admin' already exists")
END

echo "✅ Build completed successfully!"
