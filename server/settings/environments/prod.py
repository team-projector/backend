from settings import config

SECRET_KEY = config('DJANGO_SECRET_KEY')
DOMAIN_NAME = config('DOMAIN_NAME')

ALLOWED_HOSTS = [DOMAIN_NAME]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DJANGO_DATABASE_HOST'),
        'PORT': config('DJANGO_DATABASE_PORT', cast=int, default=5432),
        'CONN_MAX_AGE': config('CONN_MAX_AGE', cast=int, default=60),
    },
}

STATIC_ROOT = '/var/www/server/static'
MEDIA_ROOT = '/var/www/server/media'

GITLAB_TOKEN = config('DJANGO_GITLAB_TOKEN')

SOCIAL_AUTH_GITLAB_KEY = config('DJANGO_SOCIAL_AUTH_GITLAB_KEY')
SOCIAL_AUTH_GITLAB_SECRET = config('DJANGO_SOCIAL_AUTH_GITLAB_SECRET')
SOCIAL_AUTH_GITLAB_REDIRECT_URI = f'https://{DOMAIN_NAME}/signup/login'

SLACK_TOKEN = config('DJANGO_SLACK_TOKEN')
