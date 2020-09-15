#! /bin/bash

celery -A server.celery_app flower --url_prefix=admin/flower
