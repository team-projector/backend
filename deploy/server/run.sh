#! /bin/sh

./manage.py migrate \
  && uwsgi --ini deploy/server/uwsgi.ini --processes $UWSGI_PROCESSES_COUNT &

nginx
