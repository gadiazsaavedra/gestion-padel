#!/bin/bash
# Script para automatizar migraciones y ejecución de tests en Django

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py test "$@"
