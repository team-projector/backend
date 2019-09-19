from decouple import config

GITLAB_HOST = config(
    'DJANGO_GITLAB_HOST',
    default='https://gitlab.com'
)

GITLAB_CHECK_WEBHOOKS = config(
    'DJANGO_GITLAB_CHECK_WEBHOOKS',
    default=False,
    cast=bool
)

GITLAB_TOKEN = None

WEBHOOK_SECRET_TOKEN = None
