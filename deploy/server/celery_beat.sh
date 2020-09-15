#! /bin/bash

celery -A server.celery_app beat -s /var/run/celery_beat/schedule
