export DJANGO_SETTINGS_MODULE=config.settings
daphne config.asgi:application --bind 0.0.0.0 --port 80
