#! /bin/sh

./manage.py migrate

uwsgi --ini deploy/uwsgi.ini --processes $UWSGI_PROCESSES_COUNT &

nginx
