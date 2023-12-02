set -eux
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn --workers 2 -b 0.0.0.0:8000 Diplom.wsgi:application
