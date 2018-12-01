#! /bin/sh

./manage.py migrate

uwsgi --ini deploy/uwsgi.ini &

nginx
