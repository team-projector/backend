# -*- coding: utf-8 -*-

from decouple import config

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

STATIC_ROOT = '/var/www/static'
MEDIA_ROOT = '/var/www/media'

GITLAB_TOKEN = config('DJANGO_GITLAB_TOKEN')
WEBHOOK_SECRET_TOKEN = config('DJANGO_WEBHOOK_SECRET_TOKEN', default=None)

SOCIAL_AUTH_GITLAB_KEY = config('DJANGO_SOCIAL_AUTH_GITLAB_KEY')
SOCIAL_AUTH_GITLAB_SECRET = config('DJANGO_SOCIAL_AUTH_GITLAB_SECRET')
SOCIAL_AUTH_GITLAB_REDIRECT_URI = f'https://{DOMAIN_NAME}/signup/login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('DJANGO_EMAIL_HOST')
EMAIL_PORT = config('DJANGO_EMAIL_PORT')
EMAIL_HOST_USER = config('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DJANGO_DEFAULT_FROM_EMAIL')
