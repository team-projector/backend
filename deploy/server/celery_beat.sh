#! /bin/bash

celery -A server.celery_app beat -s /var/run/app/beat_schedule
