export DJANGO_SETTINGS_MODULE=config.settings
daphne config.asgi:application --bind localhost --port 8000
