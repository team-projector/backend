from decouple import config

SLACK_TOKEN = config('DJANGO_SLACK_TOKEN', default=None)
