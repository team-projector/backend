#! /bin/sh

./manage.py migrate

uwsgi --ini docker/server/uwsgi.ini --processes $UWSGI_PROCESSES_COUNT &

nginx
