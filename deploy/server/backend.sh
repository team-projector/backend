#! /bin/bash

set -o errexit

./manage.py initialize

nginx

WORKER_CLASS="uvicorn.workers.UvicornH11Worker"
GUNICORN_CONF="deploy/server/gunicorn_conf.py"
APP_MODULE="server.asgi"

# Start Gunicorn
exec gunicorn -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"
