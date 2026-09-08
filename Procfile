web: python manage.py migrate --noinput && python manage.py create_production_admin && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
