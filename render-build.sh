#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Configuration des variables pour le superutilisateur
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_PASSWORD=admin123
export DJANGO_SUPERUSER_EMAIL=mezui123@gmail.com

# Création automatique du superutilisateur
python manage.py createsuperuser --no-input || true
